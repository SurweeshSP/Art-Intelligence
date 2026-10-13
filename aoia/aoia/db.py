from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List
from .models import Opportunity

def _get_db_path() -> Path:
    # Always anchor to the canonical project database in the aoia directory
    canonical = Path(__file__).resolve().parent.parent / "aoia_data.db"
    return canonical

DB_PATH = _get_db_path()

class Repository:
    """Repository interface supporting SQLite (WAL, indexing, FTS5) with migration safety."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or _get_db_path()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            # Opportunities table with full indexes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id TEXT PRIMARY KEY,
                    data JSON,
                    title TEXT,
                    provider TEXT,
                    type TEXT,
                    status TEXT,
                    geo_scope TEXT,
                    deadline_date TEXT,
                    priority_score REAL,
                    fee REAL,
                    funding_level REAL,
                    source_id TEXT,
                    canonical_url TEXT,
                    content_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Ensure columns exist via safe additive migration
            existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(opportunities)").fetchall()}
            needed_cols = [
                ("title", "TEXT"),
                ("provider", "TEXT"),
                ("type", "TEXT"),
                ("priority_score", "REAL"),
                ("fee", "REAL"),
                ("funding_level", "REAL"),
                ("source_id", "TEXT"),
                ("canonical_url", "TEXT"),
                ("content_hash", "TEXT"),
                ("created_at", "TIMESTAMP"),
                ("updated_at", "TIMESTAMP")
            ]
            for col_name, col_type in needed_cols:
                if col_name not in existing_cols:
                    try:
                        conn.execute(f"ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}")
                    except Exception:
                        pass
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_deadline ON opportunities(deadline_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_geo ON opportunities(geo_scope)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_source ON opportunities(source_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_url ON opportunities(canonical_url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_hash ON opportunities(content_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_opp_priority ON opportunities(priority_score)")

            # FTS5 Virtual Table for free-text search
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS opportunities_fts USING fts5(
                        id UNINDEXED,
                        title,
                        provider,
                        type,
                        geo_scope,
                        why_text
                    )
                """)
            except Exception:
                pass

            # Sources table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    source_id TEXT PRIMARY KEY,
                    data JSON,
                    enabled INTEGER DEFAULT 1,
                    verification TEXT DEFAULT 'PENDING',
                    consecutive_failures INTEGER DEFAULT 0,
                    last_health_check TIMESTAMP,
                    health_reason TEXT,
                    records_found INTEGER DEFAULT 0
                )
            """)

            # Frontier table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS frontier (
                    url TEXT PRIMARY KEY,
                    source_id TEXT,
                    kind TEXT,
                    priority INTEGER DEFAULT 50,
                    depth INTEGER DEFAULT 0,
                    next_fetch_at TIMESTAMP,
                    last_fetched TIMESTAMP,
                    etag TEXT,
                    last_modified TEXT,
                    content_hash TEXT,
                    failure_count INTEGER DEFAULT 0,
                    discovered_via TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_frontier_source ON frontier(source_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_frontier_priority ON frontier(priority)")

            # Versions table (never overwrite history)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT,
                    version_num INTEGER,
                    snapshot JSON,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_versions_opp ON versions(opportunity_id)")

            # Runs / audit table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crawl_runs (
                    run_id TEXT PRIMARY KEY,
                    started_at TIMESTAMP,
                    ended_at TIMESTAMP,
                    status TEXT,
                    diagnostics JSON
                )
            """)

    def save_opportunity(self, opp: Opportunity):
        data_json = opp.model_dump_json()
        fee = opp.financial.application_fee
        funding = opp.financial.funding_level
        src_id = opp.source.source_id or ""
        canon_url = opp.canonical_url or opp.application_url
        content_hash = str(hash(data_json))

        with self.get_connection() as conn:
            # Check existing version
            cur = conn.execute("SELECT data FROM opportunities WHERE id = ?", (opp.id,))
            row = cur.fetchone()
            if row:
                old_data = row["data"]
                if old_data != data_json:
                    # Save version
                    v_count = conn.execute("SELECT COUNT(*) FROM versions WHERE opportunity_id = ?", (opp.id,)).fetchone()[0]
                    conn.execute(
                        "INSERT INTO versions (opportunity_id, version_num, snapshot) VALUES (?, ?, ?)",
                        (opp.id, v_count + 1, old_data)
                    )

            conn.execute("""
                INSERT OR REPLACE INTO opportunities (
                    id, data, title, provider, type, status, geo_scope, deadline_date,
                    priority_score, fee, funding_level, source_id, canonical_url, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                opp.id, data_json, opp.title, opp.provider, opp.type, opp.status,
                opp.geo_scope, opp.deadline_date, opp.priority_score, fee,
                funding, src_id, canon_url, content_hash
            ))

            # Update FTS
            try:
                conn.execute("DELETE FROM opportunities_fts WHERE id = ?", (opp.id,))
                conn.execute("""
                    INSERT INTO opportunities_fts (id, title, provider, type, geo_scope, why_text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (opp.id, opp.title, opp.provider, opp.type, opp.geo_scope, opp.why_text))
            except Exception:
                pass

    def save_opportunities_batch(self, opps: List[Opportunity]):
        if not opps:
            return
        with self.get_connection() as conn:
            records = []
            fts_records = []
            for opp in opps:
                data_json = opp.model_dump_json()
                canon = opp.canonical_url or opp.application_url
                records.append((
                    opp.id, data_json, opp.title, opp.provider, opp.type, opp.status,
                    opp.geo_scope, opp.deadline_date, opp.priority_score,
                    opp.financial.application_fee, opp.financial.funding_level,
                    opp.source.source_id or "", canon, str(hash(data_json))
                ))
                fts_records.append((
                    opp.id, opp.title, opp.provider, opp.type, opp.geo_scope, opp.why_text
                ))

            conn.executemany("""
                INSERT OR REPLACE INTO opportunities (
                    id, data, title, provider, type, status, geo_scope, deadline_date,
                    priority_score, fee, funding_level, source_id, canonical_url, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, records)

            try:
                conn.executemany("""
                    INSERT OR REPLACE INTO opportunities_fts (id, title, provider, type, geo_scope, why_text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, fts_records)
            except Exception:
                pass

    def load_all_opportunities(self) -> List[Opportunity]:
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT data FROM opportunities")
            return [Opportunity.model_validate_json(row["data"]) for row in cursor.fetchall()]

    def search_opportunities_fts(self, query: str) -> List[Opportunity]:
        if not query.strip():
            return self.load_all_opportunities()
        with self.get_connection() as conn:
            try:
                cursor = conn.execute("""
                    SELECT o.data FROM opportunities o
                    JOIN opportunities_fts f ON o.id = f.id
                    WHERE opportunities_fts MATCH ?
                """, (f"{query}*",))
                return [Opportunity.model_validate_json(row["data"]) for row in cursor.fetchall()]
            except Exception:
                # Fallback to LIKE
                cursor = conn.execute("""
                    SELECT data FROM opportunities
                    WHERE title LIKE ? OR provider LIKE ?
                """, (f"%{query}%", f"%{query}%"))
                return [Opportunity.model_validate_json(row["data"]) for row in cursor.fetchall()]

    def save_sources(self, sources: List[Dict[str, Any]]):
        with self.get_connection() as conn:
            for s in sources:
                sid = s.get("source_id")
                data_json = json.dumps(s)
                enabled = 1 if s.get("enabled", True) else 0
                verif = s.get("verification", "PENDING")
                fails = s.get("consecutive_failures", 0)
                reason = s.get("health_reason", "")
                conn.execute("""
                    INSERT OR REPLACE INTO sources (
                        source_id, data, enabled, verification, consecutive_failures, health_reason
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (sid, data_json, enabled, verif, fails, reason))

    def load_sources(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            rows = conn.execute("SELECT data FROM sources").fetchall()
            return [json.loads(r["data"]) for r in rows]

# Global DB helpers
_repo = Repository()

def init_db():
    _repo.init_db()

def save_opportunity(opp: Opportunity):
    _repo.save_opportunity(opp)

def save_opportunities_batch(opps: List[Opportunity]):
    _repo.save_opportunities_batch(opps)

def load_all_opportunities() -> List[Opportunity]:
    return _repo.load_all_opportunities()

def search_opportunities(q: str) -> List[Opportunity]:
    return _repo.search_opportunities_fts(q)

def save_sources(sources: List[Dict[str, Any]]):
    _repo.save_sources(sources)

def load_sources() -> List[Dict[str, Any]]:
    return _repo.load_sources()

def seed_demo_data():
    """Seed seed records Terrain and SAM Cycle 4."""
    init_db()
    opp1 = Opportunity(
        id="opp_seed_001",
        title="Terrain - Online work submission",
        provider="Terrain",
        type="open call",
        announcement_date="2026-07-03",
        deadline_date="2026-09-12",
        location={"city": "Delhi", "country": "IN"},
        geo_scope="INDIA",
        age_min=21,
        financial={"application_fee": 0.0, "funding_level": 0.5},
        application_url="https://www.terrain.art/",
        canonical_url="https://www.terrain.art/",
        source={"url": "https://www.terrain.art/", "tier": "T0", "discovered_via": "SEED", "source_id": "terrain"},
        status="RECENTLY_CLOSED",
        verification="CONFIRMED",
        why_text="Seed record. Deadline passed (2026-09-12).",
        bucket_label="CLOSED"
    )
    opp2 = Opportunity(
        id="opp_seed_002",
        title="Residency Cycle 4",
        provider="Singapore Art Museum",
        type="residency",
        duration="1-3 months",
        announcement_date="2026-07-12",
        deadline_date="2026-09-30",
        location={"city": "Singapore", "country": "SG"},
        geo_scope="ASIA",
        age_min=18,
        financial={"application_fee": 0.0, "funding_level": 0.8},
        application_url="https://www.singaporeartmuseum.sg/",
        canonical_url="https://www.singaporeartmuseum.sg/",
        source={"url": "https://www.singaporeartmuseum.sg/", "tier": "T0", "discovered_via": "SEED", "source_id": "sam_singapore"},
        status="RECENTLY_CLOSED",
        verification="CONFIRMED",
        why_text="Seed record. Deadline passed (2026-09-30).",
        bucket_label="CLOSED"
    )
    # Lalit Kala Akademi National Exhibition
    opp3 = Opportunity(
        id="opp_seed_003",
        title="64th National Exhibition of Art - Open Call",
        provider="Lalit Kala Akademi",
        type="open call",
        announcement_date="2026-09-01",
        deadline_date="2026-11-20",
        location={"city": "New Delhi", "country": "IN", "state": "Delhi"},
        geo_scope="INDIA",
        age_min=25,
        mediums=["painting", "sculpture", "printmaking", "ceramics"],
        financial={"application_fee": 0.0, "funding_level": 0.8},
        application_url="https://lalitkala.gov.in/event_details/339",
        canonical_url="https://lalitkala.gov.in/event_details/339",
        source={"url": "https://lalitkala.gov.in/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "lalit_kala_akademi"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Official Ministry of Culture academy open call. Fee-free with cash awards & catalogue.",
        bucket_label="PREPARE"
    )
    # Chennai Painting Fellowship (Regional Centre Chennai)
    opp4 = Opportunity(
        id="opp_seed_004",
        title="South Zone Visual Arts Fellowship 2026-27",
        provider="Lalit Kala Akademi (Regional Centre Chennai)",
        type="fellowship",
        announcement_date="2026-09-15",
        deadline_date="2026-11-30",
        location={"city": "Chennai", "country": "IN", "state": "Tamil Nadu"},
        geo_scope="CHENNAI",
        mediums=["painting", "drawing", "mixed media"],
        financial={"application_fee": 0.0, "funding_level": 1.0, "grant_or_stipend": "PROVIDED", "studio": "PROVIDED"},
        application_url="https://lalitkala.gov.in/regional-centres/chennai",
        canonical_url="https://lalitkala.gov.in/regional-centres/chennai",
        source={"url": "https://lalitkala.gov.in/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "lalit_kala_akademi"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Chennai studio residency & monthly stipend for practicing fine artists.",
        bucket_label="PREPARE"
    )
    # India Art Fair Young Artists Commission
    opp5 = Opportunity(
        id="opp_seed_005",
        title="India Art Fair Artists' Residency & Commission 2027",
        provider="India Art Fair",
        type="residency",
        announcement_date="2026-08-20",
        deadline_date="2026-12-15",
        location={"city": "New Delhi", "country": "IN"},
        geo_scope="INDIA",
        mediums=["installation", "sculpture", "mixed media", "public art"],
        financial={"application_fee": 0.0, "funding_level": 0.9, "accommodation": "PROVIDED", "grant_or_stipend": "PROVIDED"},
        application_url="https://indiaartfair.in/noticeboard",
        canonical_url="https://indiaartfair.in/noticeboard",
        source={"url": "https://indiaartfair.in/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "iaf_noticeboard"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Supported residency for visual art installations.",
        bucket_label="PLAN"
    )
    # Inlaks Fine Art Award
    opp6 = Opportunity(
        id="opp_seed_006",
        title="Inlaks Fine Art Award 2026-2027",
        provider="Inlaks Shivdasani Foundation",
        type="grant",
        announcement_date="2026-09-10",
        deadline_date="2026-10-31",
        location={"city": "Mumbai", "country": "IN"},
        geo_scope="INDIA",
        mediums=["painting", "sculpture", "drawing"],
        financial={"application_fee": 0.0, "funding_level": 1.0, "grant_or_stipend": "PROVIDED"},
        application_url="https://www.inlaksfoundation.org/art-awards/",
        canonical_url="https://www.inlaksfoundation.org/art-awards/",
        source={"url": "https://www.inlaksfoundation.org/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "inlaks"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Annual financial grant to young emerging visual artists under 30 in India.",
        bucket_label="VERY SOON"
    )
    # KHOJ International Artists' Association Residency
    opp7 = Opportunity(
        id="opp_seed_007",
        title="KHOJ Peers Residency Programme 2026",
        provider="KHOJ International Artists' Association",
        type="residency",
        announcement_date="2026-09-05",
        deadline_date="2026-11-10",
        location={"city": "New Delhi", "country": "IN"},
        geo_scope="INDIA",
        mediums=["contemporary art", "installation", "mixed media"],
        financial={"application_fee": 0.0, "funding_level": 0.9, "studio": "PROVIDED", "accommodation": "PROVIDED"},
        application_url="https://khojstudios.org/programmes/peers-2026",
        canonical_url="https://khojstudios.org/programmes/peers-2026",
        source={"url": "https://khojstudios.org/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "khoj"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Peer residency with studio space and critique mentorship.",
        bucket_label="VERY SOON"
    )
    # Serendipity Arts Festival - Closing in 5 days!
    opp8 = Opportunity(
        id="opp_seed_008",
        title="Serendipity Arts Special Visual Arts Projects Call 2026",
        provider="Serendipity Arts Foundation",
        type="grant",
        announcement_date="2026-09-15",
        deadline_date="2026-10-17",
        location={"city": "Panaji", "country": "IN", "state": "Goa"},
        geo_scope="INDIA",
        mediums=["installation", "sculpture", "painting", "mixed media"],
        financial={"application_fee": 0.0, "funding_level": 1.0, "grant_or_stipend": "PROVIDED"},
        application_url="https://serendipityarts.org/open-calls",
        canonical_url="https://serendipityarts.org/open-calls",
        source={"url": "https://serendipityarts.org/", "tier": "T0", "discovered_via": "REGISTRY", "source_id": "serendipity_arts"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Production grant and presentation at Serendipity Arts Festival. Closing in 5 days.",
        bucket_label="ACT NOW"
    )
    # Emami Art Open Call - Closing in 7 days!
    opp9 = Opportunity(
        id="opp_seed_009",
        title="Emami Art Annual Emerging Contemporary Artists Exhibition",
        provider="Emami Art",
        type="exhibition call",
        announcement_date="2026-09-20",
        deadline_date="2026-10-19",
        location={"city": "Kolkata", "country": "IN", "state": "West Bengal"},
        geo_scope="INDIA",
        mediums=["painting", "printmaking", "sculpture", "drawing"],
        financial={"application_fee": 0.0, "funding_level": 0.7},
        application_url="https://www.emamiart.com/open-call",
        canonical_url="https://www.emamiart.com/open-call",
        source={"url": "https://www.emamiart.com/", "tier": "T1", "discovered_via": "REGISTRY", "source_id": "emami_art"},
        status="OPEN",
        verification="CONFIRMED",
        why_text="Curated institutional exhibition opportunity with catalogue essay.",
        bucket_label="ACT NOW"
    )

    save_opportunity(opp1)
    save_opportunity(opp2)
    save_opportunity(opp3)
    save_opportunity(opp4)
    save_opportunity(opp5)
    save_opportunity(opp6)
    save_opportunity(opp7)
    save_opportunity(opp8)
    save_opportunity(opp9)
