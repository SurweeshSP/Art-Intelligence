from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Location(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None

class Financial(BaseModel):
    application_fee: Optional[float] = 0.0
    currency: Optional[str] = None
    funding_level: Optional[float] = None
    grant_or_stipend: str = "UNKNOWN"
    accommodation: str = "UNKNOWN"
    travel: str = "UNKNOWN"
    studio: str = "UNKNOWN"

class SourceData(BaseModel):
    url: str
    tier: str = "T0"
    discovered_via: str = "SEED"
    source_id: Optional[str] = None

class EvidenceItem(BaseModel):
    field: str
    snippet: str
    source_url: str
    confidence: float = 1.0

class Opportunity(BaseModel):
    id: str
    title: str
    provider: str
    type: str  # open call, residency, fellowship, grant, scholarship, award, exhibition call, competition, commission
    duration: Optional[str] = None
    announcement_date: Optional[str] = None
    opening_date: Optional[str] = None
    deadline_date: Optional[str] = None  # YYYY-MM-DD or UNKNOWN
    deadline_time: Optional[str] = None
    deadline_timezone: Optional[str] = None
    deadline_type: Optional[str] = None
    rolling: bool = False
    location: Location = Field(default_factory=Location)
    geo_scope: str = "UNKNOWN"  # CHENNAI, TAMIL_NADU, INDIA, ASIA, INTERNATIONAL, GLOBAL, ONLINE, UNKNOWN
    eligibility_geography: List[str] = Field(default_factory=lambda: ["UNKNOWN"])
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    career_stages: List[str] = Field(default_factory=list)
    mediums: List[str] = Field(default_factory=list)
    financial: Financial = Field(default_factory=Financial)
    requirements: List[str] = Field(default_factory=lambda: ["UNKNOWN"])
    application_url: str
    source: SourceData = Field(default_factory=lambda: SourceData(url=""))
    canonical_url: Optional[str] = None
    discovery_url: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "OPEN"  # OPEN, UPCOMING, ROLLING, DEADLINE_UNKNOWN, RECENTLY_CLOSED, EXPIRED
    verification: str = "UNVERIFIED"  # CONFIRMED, LIKELY, UNVERIFIED, VERIFICATION_REQUIRED
    last_verification_error: Optional[str] = None
    source_tier: Optional[str] = "T0"
    risk: str = "LOW"
    risk_signals: List[str] = Field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    last_changed: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    versions: List[str] = Field(default_factory=list)
    
    # Computed scores
    priority_score: float = 0.0
    why_text: str = ""
    bucket_label: str = "NO DEADLINE"
    days_left: Optional[int] = None
    fit_score: float = 0.5
