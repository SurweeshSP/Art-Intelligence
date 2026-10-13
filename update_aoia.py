import os
from pathlib import Path

base = 'aoia'

files = {
    'requirements.txt': '''\
streamlit>=1.31.0
httpx>=0.26.0
beautifulsoup4>=4.12.3
lxml>=5.1.0
selectolax>=0.3.19
trafilatura>=1.8.0
feedparser>=6.0.11
dateparser>=1.2.0
rapidfuzz>=3.6.1
pydantic>=2.6.1
pyyaml>=6.0.1
pandas>=2.2.0
plotly>=5.18.0
scikit-learn>=1.4.0
python-dateutil>=2.8.2
tzdata>=2023.4
SQLAlchemy>=2.0.25
pytest>=8.0.0
pytest-httpx>=0.28.0
respx>=0.20.2
''',
    'aoia/models.py': '''\
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class Location(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class Financial(BaseModel):
    application_fee: float = 0.0
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
    evidence: List[Dict[str, Any]] = []
    status: str = "OPEN"
    verification: str = "UNVERIFIED"
    risk: str = "LOW"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    last_changed: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    versions: List[str] = []
    priority_score: float = 0.0
    why_text: str = ""

class CollectionFlags(BaseModel):
    html: bool = False
    search: bool = False
    feed_probe: bool = False
    sitemap_probe: bool = False
    browser: bool = False

class SourceRegistryEntry(BaseModel):
    source_id: str
    name: str
    region: str
    authority_tier: str
    base_url: str
    source_type: str = "unknown"
    collection: CollectionFlags = Field(default_factory=CollectionFlags)
    priority: int = 50
    crawl_interval_minutes: int = 1440
    verification: str = "PENDING"
    origin: str = "unknown"
    pre_check: Optional[str] = None
    verification_reason: Optional[str] = None
    last_health_check: Optional[datetime] = None
    consecutive_failures: int = 0
    enabled: bool = True
''',
    'aoia/db.py': '''\
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from .models import Opportunity, SourceRegistryEntry

DB_PATH = Path("aoia_data.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, isolation_level=None) # autocommit mode
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                data JSON,
                status TEXT,
                geo_scope TEXT,
                deadline_date TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                data JSON,
                enabled INTEGER,
                consecutive_failures INTEGER
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_status ON opportunities(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_geo ON opportunities(geo_scope)")

def save_opportunity(opp: Opportunity):
    with get_conn() as conn:
        with conn:
            conn.execute(
                'INSERT OR REPLACE INTO opportunities (id, data, status, geo_scope, deadline_date) VALUES (?, ?, ?, ?, ?)',
                (opp.id, opp.model_dump_json(), opp.status, opp.geo_scope, opp.deadline_date)
            )

def load_all_opportunities() -> List[Opportunity]:
    with get_conn() as conn:
        cursor = conn.execute('SELECT data FROM opportunities')
        return [Opportunity.model_validate_json(row[0]) for row in cursor.fetchall()]
        
def save_source(source: SourceRegistryEntry):
    with get_conn() as conn:
        with conn:
            conn.execute(
                'INSERT OR REPLACE INTO sources (source_id, data, enabled, consecutive_failures) VALUES (?, ?, ?, ?)',
                (source.source_id, source.model_dump_json(), int(source.enabled), source.consecutive_failures)
            )
            
def load_sources_from_db() -> List[SourceRegistryEntry]:
    with get_conn() as conn:
        cursor = conn.execute('SELECT data FROM sources')
        return [SourceRegistryEntry.model_validate_json(row[0]) for row in cursor.fetchall()]

def seed_demo_data():
    init_db()
    opp1 = Opportunity(
        id="opp_seed_001", title="Terrain - Online work submission", provider="Terrain", type="open_call",
        announcement_date="2026-07-03", deadline_date="2026-09-12",
        location={"city": "Delhi", "country": "IN"}, geo_scope="INDIA", age_min=21,
        financial={"application_fee": 0}, application_url="https://www.terrain.art/",
        source={"url": "https://www.terrain.art/", "tier": "T0", "discovered_via": "SEED"},
        status="RECENTLY_CLOSED", verification="UNVERIFIED",
        why_text="Seed record. Deadline passed."
    )
    opp2 = Opportunity(
        id="opp_seed_002", title="Residency Cycle 4", provider="Singapore Art Museum", type="residency",
        duration="1-3 months", announcement_date="2026-07-12", deadline_date="2026-09-30",
        location={"city": "Singapore", "country": "SG"}, geo_scope="INTERNATIONAL", age_min=18,
        financial={"application_fee": 0}, application_url="https://www.singaporeartmuseum.sg/",
        source={"url": "https://www.singaporeartmuseum.sg/", "tier": "T0", "discovered_via": "SEED"},
        status="RECENTLY_CLOSED", verification="UNVERIFIED",
        why_text="Seed record. Deadline passed."
    )
    save_opportunity(opp1)
    save_opportunity(opp2)
''',
    'aoia/registry.py': '''\
import yaml
from pathlib import Path
from typing import List
from .models import SourceRegistryEntry
from . import db

def load_sources() -> List[SourceRegistryEntry]:
    path = Path("configs/sources.yaml")
    if not path.exists(): return []
    with open(path) as f:
        data = yaml.safe_load(f).get("sources", [])
    
    entries = []
    seen_ids = set()
    for item in data:
        entry = SourceRegistryEntry(**item)
        if entry.source_id in seen_ids:
            raise ValueError(f"Duplicate source_id: {entry.source_id}")
        seen_ids.add(entry.source_id)
        entries.append(entry)
        
    # Sync with DB
    existing = {s.source_id: s for s in db.load_sources_from_db()}
    for entry in entries:
        if entry.source_id in existing:
            ext = existing[entry.source_id]
            entry.verification = ext.verification
            entry.verification_reason = ext.verification_reason
            entry.last_health_check = ext.last_health_check
            entry.consecutive_failures = ext.consecutive_failures
            entry.enabled = ext.enabled
        db.save_source(entry)
        
    return entries
''',
    'aoia/health.py': '''\
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import SourceRegistryEntry
from . import db

def check_source(source: SourceRegistryEntry) -> SourceRegistryEntry:
    try:
        r = httpx.get(source.base_url, timeout=5.0, follow_redirects=True)
        if r.status_code == 200:
            source.verification = "PASSED"
            source.verification_reason = "HTTP 200 OK"
            source.consecutive_failures = 0
        else:
            source.verification = "FAILED"
            source.verification_reason = f"HTTP {r.status_code}"
            source.consecutive_failures += 1
    except Exception as e:
        source.verification = "FAILED"
        source.verification_reason = str(e)
        source.consecutive_failures += 1
        
    source.last_health_check = datetime.now(ZoneInfo("Asia/Kolkata"))
    if source.consecutive_failures >= 5:
        source.enabled = False
        source.verification_reason += " (Disabled after 5 failures)"
        
    db.save_source(source)
    return source
''',
    'aoia/frontier.py': '''\
from typing import List
from .models import SourceRegistryEntry

def get_due_sources(sources: List[SourceRegistryEntry]) -> List[SourceRegistryEntry]:
    return [s for s in sources if s.enabled and s.verification == "PASSED"]
''',
    'aoia/fetch.py': '''\
import httpx
def fetch_content(url: str) -> str:
    try:
        return httpx.get(url, timeout=10.0, follow_redirects=True).text
    except Exception:
        return ""
''',
    'aoia/detect.py': '''\
def is_opportunity_page(html: str) -> bool:
    signals = ["open call", "apply", "deadline", "residency", "fellowship", "grant"]
    text = html.lower()
    return sum(1 for s in signals if s in text) >= 2
''',
    'aoia/extract.py': '''\
from bs4 import BeautifulSoup
from .models import Opportunity, Location, SourceData

def extract_opportunity(html: str, url: str, source_tier: str) -> Opportunity:
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string if soup.title else "Discovered Opportunity"
    return Opportunity(
        id=f"opp_{hash(url)}",
        title=title,
        provider="Extracted Provider",
        type="open_call",
        location=Location(city="Unknown", country="Unknown"),
        application_url=url,
        source=SourceData(url=url, tier=source_tier, discovered_via="HTML")
    )
''',
    'aoia/normalize.py': '''\
from .models import Opportunity

def normalize_data(opp: Opportunity) -> Opportunity:
    if opp.location.city in ["Chennai", "Delhi"]:
        opp.geo_scope = "INDIA" if opp.location.city == "Delhi" else "CHENNAI"
    return opp
''',
    'aoia/validate.py': '''\
from .models import Opportunity

def validate_opportunity(opp: Opportunity) -> Opportunity:
    if opp.deadline_date:
        opp.verification = "LIKELY"
    return opp
''',
    'aoia/dedupe.py': '''\
from typing import List
from .models import Opportunity

def deduplicate(opps: List[Opportunity]) -> List[Opportunity]:
    seen = set()
    res = []
    for o in opps:
        if o.id not in seen:
            seen.add(o.id)
            res.append(o)
    return res
''',
    'aoia/status.py': '''\
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Opportunity

def compute_status(opp: Opportunity, now: datetime = None) -> Opportunity:
    if now is None:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    if not opp.deadline_date:
        opp.status = "OPEN"
        return opp
    try:
        deadline = datetime.strptime(opp.deadline_date, "%Y-%m-%d").date()
        if deadline < now.date():
            opp.status = "RECENTLY_CLOSED"
        else:
            opp.status = "OPEN"
    except Exception:
        pass
    return opp
''',
    'aoia/eligibility.py': '''\
from .models import Opportunity

def check_eligibility(opp: Opportunity, profile: dict) -> bool:
    if opp.financial.application_fee > profile.get("max_application_fee_inr", 0):
        return False
    return True
''',
    'aoia/scoring.py': '''\
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Opportunity
from typing import List

def score_and_rank(opps: List[Opportunity], profile: dict, weights: dict) -> List[Opportunity]:
    now = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    for opp in opps:
        geo_score = 1.0 if opp.geo_scope in ["CHENNAI", "TAMIL_NADU"] else (0.8 if opp.geo_scope == "INDIA" else 0.5)
        money_score = 0.4 if opp.financial.application_fee == 0 else 0.0
        date_score = 0.5
        days_left = 999
        if opp.deadline_date:
            try:
                deadline = datetime.strptime(opp.deadline_date, "%Y-%m-%d").date()
                days_left = (deadline - now).days
                if days_left >= 0:
                    date_score = 1 - min(days_left, 90) / 90
            except: pass
            
        w_g = weights.get('geo', 0.3)
        w_m = weights.get('money', 0.25)
        w_d = weights.get('date', 0.3)
        w_f = weights.get('fit', 0.15)
        
        priority = (w_g*geo_score + w_m*money_score + w_d*date_score + w_f*0.8)
        opp.priority_score = priority
        opp.why_text = f"{days_left} days left | Geo: {opp.geo_scope}"
        
    return sorted(opps, key=lambda x: (-x.priority_score))
''',
    'aoia/pipeline.py': '''\
from . import db, registry, health, frontier, fetch, detect, extract, normalize, validate, dedupe, status, eligibility, scoring
import json
import yaml
import concurrent.futures

def run_pipeline(progress_callback=None):
    if progress_callback: progress_callback("Initializing DB...")
    db.init_db()
    
    with open("configs/artist_profile.json") as f:
        profile = json.load(f)
    with open("configs/ranking.yaml") as f:
        weights = yaml.safe_load(f).get("weights", {})
        
    if progress_callback: progress_callback("Loading sources...")
    sources = registry.load_sources()
    
    if progress_callback: progress_callback("Health checks...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        checked_sources = list(executor.map(health.check_source, sources))
    
    active_sources = frontier.get_due_sources(checked_sources)
    discovered_opps = []
    
    def process_source(s):
        html = fetch.fetch_content(s.base_url)
        if detect.is_opportunity_page(html):
            opp = extract.extract_opportunity(html, s.base_url, s.authority_tier)
            opp = normalize.normalize_data(opp)
            opp = validate.validate_opportunity(opp)
            return opp
        return None

    if progress_callback: progress_callback("Fetching and parsing...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for opp in executor.map(process_source, active_sources):
            if opp: discovered_opps.append(opp)
            
    if progress_callback: progress_callback("Processing database logic...")
    all_opps = db.load_all_opportunities()
    all_opps.extend(discovered_opps)
    all_opps = dedupe.deduplicate(all_opps)
    
    for opp in all_opps:
        opp = status.compute_status(opp)
        db.save_opportunity(opp)
        
    if progress_callback: progress_callback("Scoring & Ranking...")
    valid_opps = [o for o in all_opps if eligibility.check_eligibility(o, profile)]
    ranked = scoring.score_and_rank(valid_opps, profile, weights)
    
    if progress_callback: progress_callback("Done.")
    return ranked, checked_sources
''',
    'tests/test_core.py': '''\
import pytest
from aoia import status, registry, health
from aoia.models import Opportunity, Location, SourceData, SourceRegistryEntry
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import yaml

def test_status_engine():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    past = (now - timedelta(days=10)).strftime("%Y-%m-%d")
    future = (now + timedelta(days=10)).strftime("%Y-%m-%d")
    
    o1 = Opportunity(id="1", title="test", provider="test", location=Location(), application_url="http", source=SourceData(url="http", tier="T0", discovered_via="test"), deadline_date=past)
    o2 = Opportunity(id="2", title="test", provider="test", location=Location(), application_url="http", source=SourceData(url="http", tier="T0", discovered_via="test"), deadline_date=future)
    
    o1 = status.compute_status(o1, now)
    o2 = status.compute_status(o2, now)
    
    assert o1.status == "RECENTLY_CLOSED"
    assert o2.status == "OPEN"

def test_registry_validation():
    # Write a dummy sources.yaml to test validation
    dummy_yaml = """
    sources:
      - source_id: test1
        name: test
        region: india
        authority_tier: T0
        base_url: https://test.com
    """
    with open("configs/sources.yaml", "w") as f:
        f.write(dummy_yaml)
        
    sources = registry.load_sources()
    assert len(sources) == 1
    assert sources[0].source_id == "test1"
    assert sources[0].collection.html == False

def test_health_gate(httpx_mock):
    httpx_mock.add_response(url="https://test.com", status_code=200)
    httpx_mock.add_response(url="https://fail.com", status_code=404)
    
    s1 = SourceRegistryEntry(source_id="1", name="n1", region="r1", authority_tier="T0", base_url="https://test.com")
    s2 = SourceRegistryEntry(source_id="2", name="n2", region="r1", authority_tier="T0", base_url="https://fail.com", consecutive_failures=4)
    
    health.check_source(s1)
    assert s1.verification == "PASSED"
    assert s1.consecutive_failures == 0
    
    health.check_source(s2)
    assert s2.verification == "FAILED"
    assert s2.consecutive_failures == 5
    assert s2.enabled == False
''',
    'tests/test_scale.py': '''\
import pytest
import time
from aoia import scoring, dedupe
from aoia.models import Opportunity, Location, SourceData
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def test_scale_50k_opportunities():
    start = time.time()
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    opps = []
    
    # Generate 50,000 dummy opportunities
    for i in range(50000):
        opps.append(Opportunity(
            id=f"syn_opp_{i}",
            title=f"Synthetic {i}",
            provider="SynProvider",
            type="residency",
            location=Location(city="Chennai", country="IN"),
            geo_scope="CHENNAI",
            application_url=f"https://syn.com/{i}",
            source=SourceData(url=f"https://syn.com/{i}", tier="T0", discovered_via="SYNTHETIC"),
            deadline_date=(now + timedelta(days=i%100)).strftime("%Y-%m-%d"),
            status="OPEN"
        ))
        
    gen_time = time.time() - start
    
    start_dedupe = time.time()
    deduped = dedupe.deduplicate(opps)
    dedupe_time = time.time() - start_dedupe
    
    start_score = time.time()
    profile = {"max_application_fee_inr": 0}
    weights = {"geo": 0.3, "money": 0.25, "date": 0.3, "fit": 0.15}
    ranked = scoring.score_and_rank(deduped, profile, weights)
    score_time = time.time() - start_score
    
    assert len(ranked) == 50000
    
    # Assert performance boundaries (very generous for CI)
    assert dedupe_time < 2.0
    assert score_time < 5.0
    print(f"Scale test 50k opps - Gen: {gen_time:.2f}s, Dedupe: {dedupe_time:.2f}s, Score: {score_time:.2f}s")
'''
}

for filepath, content in files.items():
    full_path = os.path.join(base, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated files.")
