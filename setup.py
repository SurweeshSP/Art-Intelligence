import os

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
''',
    'README.md': '''\
# AOIA (Art Opportunity Intelligence Agent)

AOIA is a web-only collection agent that fetches, normalizes, and ranks art opportunities (residencies, grants, open calls) based on an artist's profile, prioritizing geographic fit, funding, and impending deadlines.

## Setup & Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Streamlit App:**
   ```bash
   streamlit run app.py
   ```
3. **Usage:**
   - Configure your Artist Profile in the sidebar.
   - Click **Run AOIA now** to execute the pipeline (fetches data, updates database, scores opportunities).
   - Use the **Demo data** toggle to explore UI with sample seed records without waiting for network fetching.
''',
    'configs/sources.yaml': '''\
sources:
  - source_id: cpb_foundation
    name: Chennai Photo Biennale Foundation
    region: chennai
    authority_tier: T0
    base_url: https://chennaiphotobiennale.foundation/
    collection: {html: true, search: true}
    priority: 100
    crawl_interval_minutes: 360
    verification: PENDING

  - source_id: terrain
    name: Terrain
    region: india
    authority_tier: T0
    base_url: https://www.terrain.art/
    collection: {html: true}
    priority: 90
    crawl_interval_minutes: 720
    verification: PENDING

  - source_id: sam_singapore
    name: Singapore Art Museum
    region: international
    authority_tier: T0
    base_url: https://www.singaporeartmuseum.sg/
    collection: {html: true}
    priority: 80
    crawl_interval_minutes: 1440
    verification: PENDING
''',
    'configs/ranking.yaml': '''\
weights:
  geo: 0.30
  money: 0.25
  date: 0.30
  fit: 0.15

geo_scores:
  CHENNAI: 1.0
  TAMIL_NADU: 1.0
  INDIA: 0.8
  ASIA: 0.6
  INTERNATIONAL: 0.5
  GLOBAL: 0.5
  ONLINE: 0.5

source_trust:
  T0: 1.0
  T1: 0.85
  T2: 0.70
  T3: 0.55
  T4: 0.40
''',
    'configs/regions.yaml': '''\
regions:
  chennai: ["Chennai", "Tamil Nadu"]
  india: ["India", "IN"]
  international: ["Global", "International", "Online"]
''',
    'configs/artist_profile.json': '''\
{
  "location": {"city": "Chennai", "state": "Tamil Nadu", "country": "IN"},
  "nationality": "IN",
  "age": 25,
  "career_stage": "emerging",
  "mediums": ["installation", "sculpture", "mixed_media"],
  "themes": ["technology", "human perception", "identity", "space"],
  "income_bracket": "low",
  "max_application_fee_inr": 0,
  "opportunity_types": ["residency", "fellowship", "open_call", "grant", "exhibition"],
  "preferred_regions": ["chennai", "india", "asia", "europe", "global"],
  "travel_ok": true
}
''',
    'aoia/__init__.py': '',
    'aoia/models.py': '''\
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
    
    # Computed scores
    priority_score: float = 0.0
    why_text: str = ""
''',
    'aoia/db.py': '''\
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from .models import Opportunity

DB_PATH = Path("aoia_data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                data JSON,
                status TEXT,
                geo_scope TEXT,
                deadline_date TEXT
            )
        """)
        
def save_opportunity(opp: Opportunity):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'INSERT OR REPLACE INTO opportunities (id, data, status, geo_scope, deadline_date) VALUES (?, ?, ?, ?, ?)',
            (opp.id, opp.model_dump_json(), opp.status, opp.geo_scope, opp.deadline_date)
        )

def load_all_opportunities() -> List[Opportunity]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute('SELECT data FROM opportunities')
        return [Opportunity.model_validate_json(row[0]) for row in cursor.fetchall()]

def seed_demo_data():
    init_db()
    # Terrain
    opp1 = Opportunity(
        id="opp_seed_001", title="Terrain - Online work submission", provider="Terrain", type="open_call",
        announcement_date="2026-07-03", deadline_date="2026-09-12",
        location={"city": "Delhi", "country": "IN"}, geo_scope="INDIA", age_min=21,
        financial={"application_fee": 0}, application_url="https://www.terrain.art/",
        source={"url": "https://www.terrain.art/", "tier": "T0", "discovered_via": "SEED"},
        status="RECENTLY_CLOSED", verification="UNVERIFIED",
        why_text="Seed record. Deadline passed."
    )
    # SAM
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

def load_sources():
    path = Path("configs/sources.yaml")
    if not path.exists(): return []
    with open(path) as f:
        return yaml.safe_load(f).get("sources", [])
''',
    'aoia/health.py': '''\
import httpx

def check_source(source: dict) -> dict:
    url = source.get("base_url")
    try:
        r = httpx.get(url, timeout=5.0, follow_redirects=True)
        if r.status_code == 200:
            source["verification"] = "PASSED"
            source["health_reason"] = "HTTP 200 OK"
        else:
            source["verification"] = "FAILED"
            source["health_reason"] = f"HTTP {r.status_code}"
    except Exception as e:
        source["verification"] = "FAILED"
        source["health_reason"] = str(e)
    return source
''',
    'aoia/frontier.py': '''\
def get_due_sources(sources):
    return [s for s in sources if s.get("verification") == "PASSED"]
''',
    'aoia/fetch.py': '''\
import httpx
def fetch_content(url: str) -> str:
    try:
        return httpx.get(url, timeout=10.0, follow_redirects=True).text
    except Exception:
        return ""
''',
    'aoia/discovery.py': '''\
def discover_links(html: str, base_url: str) -> list:
    return [base_url] # Stub
''',
    'aoia/detect.py': '''\
def is_opportunity_page(html: str) -> bool:
    signals = ["open call", "apply", "deadline", "residency", "fellowship", "grant"]
    text = html.lower()
    return sum(1 for s in signals if s in text) >= 2
''',
    'aoia/extract.py': '''\
from bs4 import BeautifulSoup
from .models import Opportunity

def extract_opportunity(html: str, url: str) -> Opportunity:
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.string if soup.title else "Discovered Opportunity"
    return Opportunity(
        id=f"opp_{hash(url)}",
        title=title,
        provider="Extracted Provider",
        type="open_call",
        location={"city": "Unknown", "country": "Unknown"},
        application_url=url,
        source={"url": url, "tier": "T4", "discovered_via": "HTML"}
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
def deduplicate(opps: list) -> list:
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

def compute_status(opp: Opportunity) -> Opportunity:
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
    'aoia/embeddings.py': '''\
from .models import Opportunity

def calculate_fit(opp: Opportunity, profile: dict) -> float:
    return 0.8 # Stub
''',
    'aoia/scoring.py': '''\
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Opportunity

def score_and_rank(opps: list[Opportunity], profile: dict, weights: dict) -> list[Opportunity]:
    now = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    for opp in opps:
        # Geo
        geo_score = 1.0 if opp.geo_scope in ["CHENNAI", "TAMIL_NADU"] else (0.8 if opp.geo_scope == "INDIA" else 0.5)
        
        # Money
        money_score = 0.4 if opp.financial.application_fee == 0 else 0.0
        
        # Date
        date_score = 0.5
        days_left = 999
        if opp.deadline_date:
            try:
                deadline = datetime.strptime(opp.deadline_date, "%Y-%m-%d").date()
                days_left = (deadline - now).days
                if days_left >= 0:
                    date_score = 1 - min(days_left, 90) / 90
            except: pass
            
        # Fit
        fit_score = 0.8
        
        w_g = weights.get('geo', 0.3)
        w_m = weights.get('money', 0.25)
        w_d = weights.get('date', 0.3)
        w_f = weights.get('fit', 0.15)
        
        priority = (w_g*geo_score + w_m*money_score + w_d*date_score + w_f*fit_score)
        opp.priority_score = priority
        opp.why_text = f"{days_left} days left | Fit: {int(fit_score*100)}% | Geo: {opp.geo_scope}"
        
    return sorted(opps, key=lambda x: (-x.priority_score))
''',
    'aoia/risk.py': '''\
from .models import Opportunity
def assess_risk(opp: Opportunity): pass
''',
    'aoia/changes.py': '''\
from .models import Opportunity
def detect_changes(new_opp: Opportunity, old_opp: Opportunity): pass
''',
    'aoia/recurrence.py': '''\
def predict_cycles(opps: list): pass
''',
    'aoia/snapshot.py': '''\
def create_snapshot(opps: list): pass
''',
    'aoia/pipeline.py': '''\
from . import db, registry, health, frontier, fetch, discovery, detect, extract, normalize, validate, dedupe, status, eligibility, embeddings, scoring
import json
import yaml

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
    checked_sources = [health.check_source(s) for s in sources]
    
    active_sources = frontier.get_due_sources(checked_sources)
    discovered_opps = []
    
    for idx, s in enumerate(active_sources):
        if progress_callback: progress_callback(f"Fetching {s['name']}...")
        html = fetch.fetch_content(s['base_url'])
        if detect.is_opportunity_page(html):
            opp = extract.extract_opportunity(html, s['base_url'])
            opp = normalize.normalize_data(opp)
            opp = validate.validate_opportunity(opp)
            discovered_opps.append(opp)
            
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
    'app.py': '''\
import streamlit as st
import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

from aoia import pipeline, db

st.set_page_config(page_title="AOIA Dashboard", layout="wide")

# Init DB on first load
db.init_db()

st.sidebar.title("AOIA Settings")

# Demo Data toggle
use_demo = st.sidebar.checkbox("Use Demo Data (Seed Records)", value=True)
if use_demo:
    db.seed_demo_data()

# Load Profile
try:
    with open("configs/artist_profile.json") as f:
        profile = json.load(f)
except:
    profile = {}

st.sidebar.subheader("Artist Profile")
st.sidebar.text(f"Location: {profile.get('location', {}).get('city')}")
st.sidebar.text(f"Mediums: {', '.join(profile.get('mediums', []))}")

if st.sidebar.button("Run AOIA now", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def cb(msg):
        status_text.text(msg)
        
    ranked_opps, sources = pipeline.run_pipeline(progress_callback=cb)
    st.session_state['ranked'] = ranked_opps
    st.session_state['sources'] = sources
    progress_bar.progress(100)
    status_text.text("Run complete!")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard", "Ranked Lists", "Closing Soon", "New & Changes", "Recently Closed", "Sources"
])

def render_opps_table(opps):
    if not opps:
        st.write("No opportunities found.")
        return
    df = pd.DataFrame([{
        "Title": o.title,
        "Provider": o.provider,
        "Deadline": o.deadline_date,
        "Status": o.status,
        "Geo": o.geo_scope,
        "Priority": round(o.priority_score, 2),
        "Why": o.why_text,
        "URL": o.application_url
    } for o in opps])
    st.dataframe(df, use_container_width=True)

with tab1:
    st.header("AOIA Dashboard")
    st.write(f"**Current Time (IST):** {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Opportunities", len(opps))
    col2.metric("Open", len([o for o in opps if o.status == "OPEN"]))
    col3.metric("Recently Closed", len([o for o in opps if o.status == "RECENTLY_CLOSED"]))

with tab2:
    st.header("Ranked Opportunities")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    open_opps = sorted([o for o in opps if o.status == "OPEN"], key=lambda x: -x.priority_score)
    render_opps_table(open_opps)

with tab5:
    st.header("Recently Closed (Test Rule)")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    closed_opps = [o for o in opps if o.status == "RECENTLY_CLOSED"]
    render_opps_table(closed_opps)

with tab6:
    st.header("Source Health")
    sources = st.session_state.get('sources', [])
    if sources:
        df = pd.DataFrame([{
            "Name": s['name'],
            "URL": s['base_url'],
            "Tier": s['authority_tier'],
            "Status": s.get('verification', 'PENDING'),
            "Reason": s.get('health_reason', '')
        } for s in sources])
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Run the pipeline to check sources.")
''',
    'tests/test_core.py': '''\
from aoia import status
from aoia.models import Opportunity
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def test_status_engine():
    now = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    past = (now - timedelta(days=10)).strftime("%Y-%m-%d")
    future = (now + timedelta(days=10)).strftime("%Y-%m-%d")
    
    o1 = Opportunity(id="1", title="test", provider="test", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date=past)
    o2 = Opportunity(id="2", title="test", provider="test", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date=future)
    
    o1 = status.compute_status(o1)
    o2 = status.compute_status(o2)
    
    assert o1.status == "RECENTLY_CLOSED"
    assert o2.status == "OPEN"
'''
}

os.makedirs(base, exist_ok=True)
for filepath, content in files.items():
    full_path = os.path.join(base, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Successfully created project at {os.path.abspath(base)}")
