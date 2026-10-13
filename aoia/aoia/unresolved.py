from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import httpx
import yaml
from .health import check_source_health
from .registry import validate_registry_dict

THIRD_PARTY_BLOCKED = [
    "wikipedia.org", "tripadvisor.com", "artisera.com", "facebook.com",
    "instagram.com", "twitter.com", "linkedin.com", "indiatourism.gov.in",
    "thehindu.com", "timesofindia.indiatimes.com", "indianexpress.com",
    "ndtv.com", "deccanherald.com", "google.com", "bing.com", "yahoo.com"
]

def is_third_party_listing(url: str) -> bool:
    """Check if URL belongs to Wikipedia, tourism, marketplace, or news listings."""
    from urllib.parse import urlparse
    host = urlparse(url).netloc.lower()
    return any(blocked in host for blocked in THIRD_PARTY_BLOCKED)

def token_match_in_domain_or_page(name: str, url: str, page_title: str, text: str) -> bool:
    """Accept candidate URL only if domain contains distinctive token or page title/h1/footer names it."""
    from urllib.parse import urlparse
    tokens = [t.lower() for t in re.findall(r"\w+", name) if len(t) > 3 and t.lower() not in ("arts", "gallery", "centre", "center", "trust", "society", "academy", "foundation", "institute")]
    if not tokens:
        tokens = [t.lower() for t in re.findall(r"\w+", name) if len(t) > 2]

    host = urlparse(url).netloc.lower()
    # Check domain
    if any(tok in host for tok in tokens):
        return True

    # Check page title
    title_low = page_title.lower()
    if any(tok in title_low for tok in tokens):
        return True

    # Check first 2000 chars of body
    text_low = text[:2000].lower()
    if any(tok in text_low for tok in tokens):
        return True

    return False

def discover_candidate_url_for_unresolved(
    unresolved: Dict[str, Any],
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Run discovery queries for an unresolved source and return candidate if passing all rules."""
    queries = unresolved.get("discovery_queries", [])
    if not queries:
        return None

    api_key = api_key or os.environ.get("BRAVE_API_KEY")
    candidates = []

    if api_key:
        try:
            for q in queries[:2]:
                headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
                resp = httpx.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params={"q": q}, timeout=8.0)
                if resp.status_code == 200:
                    results = resp.json().get("web", {}).get("results", [])
                    for r in results:
                        u = r.get("url")
                        if u and not is_third_party_listing(u):
                            candidates.append(u)
        except Exception:
            pass

    # Validate candidates against rules:
    # 1. Not third party listing
    # 2. Domain / title matches name token
    # 3. Health gate passes
    for cand_url in candidates:
        if is_third_party_listing(cand_url):
            continue
        try:
            resp = httpx.get(cand_url, timeout=6.0, follow_redirects=True, headers={"User-Agent": "AOIA-Bot/1.0"})
            if resp.status_code == 200:
                soup_text = resp.text[:4000]
                if token_match_in_domain_or_page(unresolved["name"], cand_url, "", soup_text):
                    # Run health check
                    mock_s = {"base_url": cand_url}
                    checked = check_source_health(mock_s)
                    if checked.get("verification") == "PASSED":
                        return {
                            "source_id": unresolved["source_id"],
                            "name": unresolved["name"],
                            "candidate_url": cand_url,
                            "title_preview": resp.text[:100],
                            "health_reason": checked.get("health_reason")
                        }
        except Exception:
            continue

    return None

def promote_unresolved_source(
    sources_yaml_path: str | Path,
    source_id: str,
    approved_url: str
) -> bool:
    """Promote an unresolved source to sources list in sources.yaml safely with backup."""
    path = Path(sources_yaml_path)
    if not path.exists():
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Backup first
    backup_path = path.with_suffix(".yaml.bak")
    with open(backup_path, "w", encoding="utf-8") as bf:
        yaml.safe_dump(data, bf, sort_keys=False)

    unresolved_list = data.get("unresolved_sources", [])
    target = None
    target_idx = -1
    for idx, u in enumerate(unresolved_list):
        if u.get("source_id") == source_id:
            target = u
            target_idx = idx
            break

    if target is None:
        return False

    # Remove from unresolved
    unresolved_list.pop(target_idx)

    # Convert to resolved source
    new_source = dict(target)
    new_source["base_url"] = approved_url
    new_source["enabled"] = True
    new_source["verification"] = "PENDING"
    new_source["crawl_interval_minutes"] = 720
    new_source["priority"] = 75
    new_source.pop("url_status", None)
    new_source.pop("why_not_enabled", None)
    new_source.pop("discovery_queries", None)

    data["sources"].append(new_source)

    # Validate before saving
    errs = validate_registry_dict(data)
    if errs:
        # Revert from backup
        with open(backup_path, "r", encoding="utf-8") as bf:
            data = yaml.safe_load(bf)
        raise ValueError(f"Promotion failed validation: {errs}")

    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    return True
