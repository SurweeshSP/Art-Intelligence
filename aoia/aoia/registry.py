"""Registry v4 loader, models, and validation logic."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse
import yaml
from pydantic import BaseModel, Field

REGIONS = {"chennai", "india", "international"}
TIERS = {"T0", "T1", "T2", "T3", "T4"}
FITS = {"HIGH", "MED", "LOW"}
ROLES = {"organiser", "funder", "venue", "sales", "discovery"}
GEO_BASES = {"registry", "text"}
CAREER_LEVELS = {"beginner", "intermediate", "standard", "any"}

class CollectionConfig(BaseModel):
    html: bool = True
    search: bool = False
    feed_probe: bool = False
    sitemap_probe: bool = False
    browser: bool = False

class DefaultsConfig(BaseModel):
    crawl_depth: int = 2
    max_pages_per_source: int = 60
    per_domain_delay_seconds: float = 2.0
    anchor_vocab: List[str] = Field(default_factory=list)
    anchor_vocab_negative: List[str] = Field(default_factory=list)

class MediumFilterConfig(BaseModel):
    include: List[str] = Field(default_factory=list)
    exclude: List[str] = Field(default_factory=list)
    rule: Optional[str] = None

class DetailIdProbe(BaseModel):
    seen: List[Any] = Field(default_factory=list)
    window: int = 50

class SourceModel(BaseModel):
    source_id: str
    name: str
    region: str
    authority_tier: str
    base_url: str
    source_type: str = "general"
    channel_role: str = "organiser"
    fine_arts_fit: str = "HIGH"
    geo_basis: str = "registry"
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    enabled: bool = True
    disabled_reason: Optional[str] = None
    verification: str = "PENDING"
    origin: str = "user_list"
    crawl_interval_minutes: int = 720
    priority: int = 50
    discovery_only: bool = False
    collection: CollectionConfig = Field(default_factory=CollectionConfig)
    career_level: List[str] = Field(default_factory=lambda: ["any"])
    career_level_confidence: Optional[str] = None
    crawl_depth: Optional[int] = None
    max_pages_per_source: Optional[int] = None
    seed_anchor_labels: List[str] = Field(default_factory=list)
    regional_centres: List[str] = Field(default_factory=list)
    detail_url_patterns: List[str] = Field(default_factory=list)
    detail_id_probe: Optional[DetailIdProbe] = None
    digest_url_patterns: List[str] = Field(default_factory=list)
    listing_urls: List[str] = Field(default_factory=list)
    extra_endpoints: List[str] = Field(default_factory=list)
    same_domain_as: Optional[str] = None
    list_section: Optional[str] = None
    notes: Optional[str] = None
    health_reason: Optional[str] = None
    consecutive_failures: int = 0
    last_health_check: Optional[str] = None
    records_found: int = 0

class UnresolvedSourceModel(BaseModel):
    source_id: str
    name: str
    region: str
    authority_tier: str
    source_type: str = "general"
    channel_role: str = "organiser"
    fine_arts_fit: str = "HIGH"
    geo_basis: str = "registry"
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    enabled: bool = False
    verification: str = "PENDING"
    origin: str = "user_list"
    discovery_queries: List[str] = Field(default_factory=list)
    career_level: List[str] = Field(default_factory=list)
    career_level_confidence: Optional[str] = None
    list_section: Optional[str] = None
    notes: Optional[str] = None
    url_status: Optional[str] = None
    why_not_enabled: Optional[str] = None

class RegistryConfig(BaseModel):
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    medium_filter: MediumFilterConfig = Field(default_factory=MediumFilterConfig)
    sources: List[SourceModel] = Field(default_factory=list)
    unresolved_sources: List[UnresolvedSourceModel] = Field(default_factory=list)

def validate_registry_dict(d: Dict[str, Any]) -> List[str]:
    """Validate registry data structure with all v4 rules. Returns list of errors."""
    errs: List[str] = []
    ids: Set[str] = set()
    urls: Set[str] = set()

    sources = d.get("sources", [])
    if not isinstance(sources, list):
        return ["'sources' section must be a list"]

    REQ = [
        "source_id", "name", "region", "authority_tier", "base_url", "source_type",
        "channel_role", "fine_arts_fit", "geo_basis", "country", "enabled",
        "verification", "origin", "crawl_interval_minutes", "priority"
    ]

    for s in sources:
        i = s.get("source_id", "?")
        for k in REQ:
            if s.get(k) is None:
                errs.append(f"{i}: missing {k}")
        if i in ids:
            errs.append(f"{i}: duplicate id")
        ids.add(i)

        u = (s.get("base_url") or "").rstrip("/")
        parsed = urlparse(u)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            errs.append(f"{i}: bad url {u}")
        if u in urls:
            errs.append(f"{i}: duplicate url")
        urls.add(u)

        if s.get("region") not in REGIONS:
            errs.append(f"{i}: invalid region '{s.get('region')}'")
        if s.get("authority_tier") not in TIERS:
            errs.append(f"{i}: invalid tier '{s.get('authority_tier')}'")
        if s.get("fine_arts_fit") not in FITS:
            errs.append(f"{i}: invalid fit '{s.get('fine_arts_fit')}'")
        if s.get("channel_role") not in ROLES:
            errs.append(f"{i}: invalid role '{s.get('channel_role')}'")
        if s.get("geo_basis") not in GEO_BASES:
            errs.append(f"{i}: invalid geo_basis '{s.get('geo_basis')}'")
        if s.get("discovery_only") and s.get("geo_basis") != "text":
            errs.append(f"{i}: discovery_only needs geo_basis=text")
        if s.get("fine_arts_fit") == "LOW" and s.get("enabled"):
            errs.append(f"{i}: LOW fit should be disabled")
        if not s.get("enabled") and not s.get("disabled_reason"):
            errs.append(f"{i}: disabled without reason")
        if s.get("verification") != "PENDING":
            errs.append(f"{i}: verification must start PENDING")
        if s.get("region") == "chennai" and s.get("country") != "IN":
            errs.append(f"{i}: chennai region needs country IN")

    for s in d.get("unresolved_sources", []):
        i = s.get("source_id", "?")
        if i in ids:
            errs.append(f"{i}: unresolved duplicates a resolved id")
        if s.get("base_url"):
            errs.append(f"{i}: unresolved entry must not have base_url")
        if not s.get("discovery_queries"):
            errs.append(f"{i}: no discovery_queries")

    return errs

def _resolve_config_path(path: str | Path) -> Path:
    p = Path(path)
    if p.exists():
        return p
    # Try relative to the aoia directory if run from repo root
    package_dir = Path(__file__).resolve().parent.parent
    candidate = package_dir / path
    if candidate.exists():
        return candidate
    candidate_configs = package_dir / "configs" / p.name
    if candidate_configs.exists():
        return candidate_configs
    return p

def validate_registry_file(path: str | Path = "configs/sources.yaml") -> List[str]:
    resolved = _resolve_config_path(path)
    if not resolved.exists():
        return [f"File not found: {path} (resolved: {resolved})"]
    with open(resolved, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return validate_registry_dict(data)

def load_registry(path: str | Path = "configs/sources.yaml") -> RegistryConfig:
    resolved = _resolve_config_path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Registry not found: {path} (tried {resolved})")
    with open(resolved, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    
    errs = validate_registry_dict(raw)
    if errs:
        raise ValueError(f"Registry validation failed ({len(errs)} errors):\n" + "\n".join(errs))
    
    return RegistryConfig.model_validate(raw)

def load_sources(path: str | Path = "configs/sources.yaml") -> List[Dict[str, Any]]:
    """Legacy helper returning enabled sources as dicts."""
    reg = load_registry(path)
    return [s.model_dump() for s in reg.sources if s.enabled]
