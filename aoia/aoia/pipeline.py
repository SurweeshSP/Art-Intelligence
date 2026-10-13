from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo
import httpx

from . import db, registry, health, fetch, documents, expansion, extract, medium_filter, dedupe, status, scoring
from .models import Opportunity

async def crawl_source_async(
    client: httpx.AsyncClient,
    source: Dict[str, Any],
    defaults: Dict[str, Any],
    filter_config: Dict[str, Any],
    report: Dict[str, Any]
) -> List[Opportunity]:
    """Crawl a single source polite, incremental, deep through all pipeline stages."""
    base_url = source.get("base_url")
    if not base_url or not source.get("enabled"):
        return []

    # 1. Seeds
    seeds = [base_url]
    seeds.extend(source.get("listing_urls", []))
    seeds.extend(source.get("extra_endpoints", []))

    # ID Probes if configured
    detail_patterns = source.get("detail_url_patterns", [])
    probe_cfg = source.get("detail_id_probe")
    if detail_patterns and probe_cfg:
        seen_ids = probe_cfg.get("seen", [])
        window = probe_cfg.get("window", 50)
        for pat in detail_patterns:
            if "{id}" in pat:
                seeds.extend(expansion.generate_id_probes(pat, seen_ids, window))

    max_pages = source.get("max_pages_per_source") or defaults.get("max_pages_per_source", 60)
    anchor_vocab = defaults.get("anchor_vocab", [])
    anchor_vocab_neg = defaults.get("anchor_vocab_negative", [])
    seed_anchors = source.get("seed_anchor_labels", [])

    pages_visited = 0
    urls_to_visit = list(dict.fromkeys(seeds))[:max_pages]
    discovered_opps: List[Opportunity] = []

    consecutive_404s = 0

    for url in urls_to_visit:
        if pages_visited >= max_pages:
            break
        pages_visited += 1

        # Fetch
        fetch_res = await fetch.async_fetch_url(client, url)
        status_code = fetch_res["status_code"]

        if status_code == 404:
            consecutive_404s += 1
            if consecutive_404s >= 5 and "event_details" in url:
                # Stop ID probe after 5 consecutive 404s
                break
        else:
            consecutive_404s = 0

        html_text = fetch_res["text"]
        if not html_text:
            continue

        # Classify
        title, text_content, kind = documents.parse_html_document(html_text, url)
        report["by_kind"][kind] = report["by_kind"].get(kind, 0) + 1

        # 1. NOT_FOUND -> drop
        if kind == "NOT_FOUND":
            continue

        # 2. HOMEPAGE / LISTING -> crawl seeds, expand links
        if kind in ("HOMEPAGE", "LISTING"):
            sub_links = expansion.filter_seed_links(
                html=html_text,
                base_url=url,
                anchor_vocab=anchor_vocab,
                anchor_vocab_negative=anchor_vocab_neg,
                seed_anchor_labels=seed_anchors
            )
            for sub_url in sub_links:
                if sub_url not in urls_to_visit and len(urls_to_visit) < max_pages:
                    urls_to_visit.append(sub_url)

        # 3. DIGEST -> split into items, resolve outbound link
        if kind == "DIGEST":
            items = expansion.expand_digest_page(html_text, url)
            for it in items:
                outbound = it["outbound_url"]
                # Fetch outbound item official page
                out_res = await fetch.async_fetch_url(client, outbound)
                if out_res["status_code"] == 200:
                    o_title, o_text, o_kind = documents.parse_html_document(out_res["text"], outbound)
                    if o_kind == "DETAIL":
                        keep, incs, excs = medium_filter.filter_by_medium(o_title + " " + o_text, filter_config)
                        if keep:
                            opp = extract.extract_opportunity_details(out_res["text"], outbound, source)
                            if opp:
                                opp.mediums = incs
                                discovered_opps.append(opp)
                    else:
                        # Unresolved item stays UNVERIFIED
                        keep, incs, excs = medium_filter.filter_by_medium(it["title"] + " " + it["text"], filter_config)
                        if keep:
                            opp = extract.extract_opportunity_details(it["text"], outbound, source)
                            if opp:
                                opp.title = it["title"]
                                opp.verification = "UNVERIFIED"
                                opp.mediums = incs
                                discovered_opps.append(opp)

        # 4. DETAIL -> evaluate medium filter & extract
        if kind == "DETAIL":
            keep, incs, excs = medium_filter.filter_by_medium(title + " " + text_content, filter_config)
            if not keep:
                report["skipped_medium"] += 1
                continue
            
            opp = extract.extract_opportunity_details(html_text, url, source)
            if opp:
                opp.mediums = incs
                discovered_opps.append(opp)

    report["pages_visited"] = pages_visited
    report["records_found"] = len(discovered_opps)
    return discovered_opps

async def run_pipeline_async(progress_callback: Optional[Callable[[str], None]] = None) -> Tuple[List[Opportunity], List[Dict[str, Any]], Dict[str, Any]]:
    """Full asynchronous crawl pipeline."""
    start_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    if progress_callback:
        progress_callback("Initializing Database and Schema...")
    db.init_db()

    # Load registry
    if progress_callback:
        progress_callback("Loading Registry v4...")
    reg = registry.load_registry("configs/sources.yaml")
    defaults = reg.defaults.model_dump()
    filter_cfg = reg.medium_filter.model_dump()

    # Health Checks
    if progress_callback:
        progress_callback("Running Health Gate checks...")
    checked_sources: List[Dict[str, Any]] = []
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for s in reg.sources:
            s_dict = s.model_dump()
            # Fast check if enabled
            if s_dict.get("enabled"):
                s_dict = health.check_source_health(s_dict)
            checked_sources.append(s_dict)

        # Filter enabled and passed sources
        active_sources = [s for s in checked_sources if s.get("enabled") and s.get("verification") == "PASSED"]

        # Crawl reports
        reports: Dict[str, Any] = {}
        all_discovered: List[Opportunity] = []

        total_active = len(active_sources)
        for idx, src in enumerate(active_sources):
            if progress_callback:
                progress_callback(f"Crawling ({idx+1}/{total_active}): {src['name']}...")
            rep = {"by_kind": {}, "skipped_medium": 0, "pages_visited": 0, "records_found": 0}
            try:
                opps = await crawl_source_async(client, src, defaults, filter_cfg, rep)
                all_discovered.extend(opps)
            except Exception as e:
                rep["error"] = str(e)
            reports[src["source_id"]] = rep

    # Deduplicate
    if progress_callback:
        progress_callback("Deduplicating and merging records...")
    existing = db.load_all_opportunities()
    combined = dedupe.deduplicate(existing + all_discovered)

    # Compute Status
    if progress_callback:
        progress_callback("Computing Status and Expiration Buckets...")
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
    processed = []
    for opp in combined:
        opp = status.compute_status(opp, now_ist)
        processed.append(opp)

    # Save Batch to DB
    db.save_opportunities_batch(processed)

    # Score and Rank
    if progress_callback:
        progress_callback("Scoring and Ranking...")
    ranked = scoring.score_and_rank(processed)

    # Persist Sources status to DB
    db.save_sources(checked_sources)

    duration = (datetime.now(ZoneInfo("Asia/Kolkata")) - start_time).total_seconds()
    diagnostics = {
        "sources_enabled": sum(1 for s in checked_sources if s.get("enabled")),
        "sources_passed": len(active_sources),
        "total_records": len(ranked),
        "duration_seconds": round(duration, 2),
        "per_source_reports": reports
    }

    if progress_callback:
        progress_callback(f"Crawl Completed in {round(duration, 1)}s!")

    return ranked, checked_sources, diagnostics

def run_pipeline(progress_callback: Optional[Callable[[str], None]] = None):
    """Synchronous entry point."""
    return asyncio.run(run_pipeline_async(progress_callback))
