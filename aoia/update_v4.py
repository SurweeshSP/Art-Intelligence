import os

def rewrite(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

rewrite("aoia/models.py", """\
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Location(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class Financial(BaseModel):
    application_fee: Optional[float] = 0.0
    currency: Optional[str] = None
    grant_or_stipend: str = "UNKNOWN"
    accommodation: str = "UNKNOWN"
    travel: str = "UNKNOWN"
    studio: str = "UNKNOWN"

class SourceData(BaseModel):
    url: str
    tier: str
    discovered_via: str

class Opportunity(BaseModel):
    id: str
    title: str
    provider: str
    type: str
    duration: Optional[str] = None
    announcement_date: Optional[str] = None
    opening_date: Optional[str] = None
    deadline_date: Optional[str] = None
    deadline_time: Optional[str] = None
    deadline_timezone: Optional[str] = None
    deadline_type: Optional[str] = None
    rolling: bool = False
    location: Location
    geo_scope: str = "INTERNATIONAL"
    eligibility_geography: List[str] = ["UNKNOWN"]
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    career_stages: List[str] = []
    mediums: List[str] = []
    financial: Financial = Field(default_factory=Financial)
    requirements: List[str] = ["UNKNOWN"]
    application_url: str
    source: SourceData
    canonical_url: Optional[str] = None
    discovery_url: Optional[str] = None
    evidence: List[Dict[str, Any]] = []
    status: str = "OPEN"
    verification: str = "UNVERIFIED"
    last_verification_error: Optional[str] = None
    source_tier: Optional[int] = None
    risk: str = "LOW"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    last_changed: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    versions: List[str] = []
    
    # Computed scores
    priority_score: float = 0.0
    why_text: str = ""
""")

rewrite("aoia/discovery.py", """\
import os
import httpx
from typing import List

def brave_search(query: str) -> List[str]:
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        return []
    try:
        headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": api_key}
        response = httpx.get("https://api.search.brave.com/res/v1/web/search", headers=headers, params={"q": query})
        if response.status_code == 200:
            data = response.json()
            return [result["url"] for result in data.get("web", {}).get("results", [])]
    except Exception as e:
        print(f"Brave Search Error: {e}")
    return []

def run_discovery() -> List[str]:
    queries = ["artist residency open call 2026 deadline", "visual artist grant India applications open"]
    urls = []
    for q in queries:
        urls.extend(brave_search(q))
    return list(set(urls))
""")

rewrite("aoia/pipeline.py", """\
from . import db, registry, health, frontier, fetch, discovery, detect, extract, normalize, validate, dedupe, status, eligibility, embeddings, scoring
import json
import yaml
import time

def run_pipeline(progress_callback=None):
    start_time = time.time()
    diagnostics = {
        "sources_enabled": 0, "sources_attempted": 0, "pages_fetched": 0, 
        "candidates_rejected": 0, "duplicates_merged": 0, "verified_opportunities": 0
    }
    if progress_callback: progress_callback("Initializing DB...")
    db.init_db()
    
    with open("configs/artist_profile.json") as f:
        profile = json.load(f)
    with open("configs/ranking.yaml") as f:
        weights = yaml.safe_load(f).get("weights", {})
        
    if progress_callback: progress_callback("Loading sources...")
    sources = registry.load_sources()
    diagnostics["sources_enabled"] = len(sources)
    
    if progress_callback: progress_callback("Health checks...")
    checked_sources = [health.check_source(s) for s in sources]
    diagnostics["sources_attempted"] = len(checked_sources)
    
    active_sources = frontier.get_due_sources(checked_sources)
    discovered_opps = []
    
    if progress_callback: progress_callback("Running web discovery...")
    discovery_urls = discovery.run_discovery()
    
    for idx, s in enumerate(active_sources):
        if progress_callback: progress_callback(f"Fetching {s['name']}...")
        urls_to_fetch = [s['base_url']] + s.get('extra_endpoints', [])
        for url in urls_to_fetch:
            html = fetch.fetch_content(url)
            diagnostics["pages_fetched"] += 1
            if detect.is_opportunity_page(html, url):
                opp = extract.extract_opportunity(html, url)
                opp = normalize.normalize_data(opp)
                opp = validate.validate_opportunity(opp)
                discovered_opps.append(opp)
            else:
                diagnostics["candidates_rejected"] += 1
                
    for url in discovery_urls:
        html = fetch.fetch_content(url)
        diagnostics["pages_fetched"] += 1
        if detect.is_opportunity_page(html, url):
            opp = extract.extract_opportunity(html, url)
            opp.verification = "UNVERIFIED"
            opp = normalize.normalize_data(opp)
            discovered_opps.append(opp)
            
    if progress_callback: progress_callback("Processing database logic...")
    all_opps = db.load_all_opportunities()
    pre_dedupe_len = len(all_opps) + len(discovered_opps)
    all_opps.extend(discovered_opps)
    all_opps = dedupe.deduplicate(all_opps)
    diagnostics["duplicates_merged"] = pre_dedupe_len - len(all_opps)
    
    for opp in all_opps:
        opp = status.compute_status(opp)
        db.save_opportunity(opp)
        
    if progress_callback: progress_callback("Scoring & Ranking...")
    valid_opps = [o for o in all_opps if eligibility.check_eligibility(o, profile)]
    ranked = scoring.score_and_rank(valid_opps, profile, weights)
    
    diagnostics["verified_opportunities"] = len([o for o in ranked if o.verification == "VERIFIED"])
    diagnostics["duration"] = round(time.time() - start_time, 2)
    
    if progress_callback: progress_callback("Done.")
    return ranked, checked_sources, diagnostics
""")
