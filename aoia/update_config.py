import json
import yaml

# 1. Update Artist Profile
with open("configs/artist_profile.json", "r", encoding="utf-8") as f:
    profile = json.load(f)

profile["mediums"] = [
    "painting",
    "design",
    "installation",
    "sculpture",
    "mixed_media"
]

with open("configs/artist_profile.json", "w", encoding="utf-8") as f:
    json.dump(profile, f, indent=2)

# 2. Append to sources.yaml
new_sources = [
    {
        "source_id": "tn_art_culture",
        "name": "Tamil Nadu Department of Art and Culture",
        "base_url": "https://artandculture.tn.gov.in/",
        "authority_tier": "T0",
        "region": "chennai",
        "source_type": "official",
        "country": "IN",
        "enabled": True,
        "discovery_only": False,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    },
    {
        "source_id": "fcea",
        "name": "Foundation for Contemporary & Emerging Art",
        "base_url": "https://fcea.in/",
        "authority_tier": "T1",
        "region": "india",
        "source_type": "official",
        "country": "IN",
        "enabled": True,
        "discovery_only": False,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    },
    {
        "source_id": "pdaf",
        "name": "Prafulla Dahanukar Art Foundation",
        "base_url": "https://www.prafullaartfoundation.org/application-page",
        "authority_tier": "T1",
        "region": "india",
        "source_type": "official",
        "country": "IN",
        "enabled": True,
        "discovery_only": False,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    },
    {
        "source_id": "iaadb",
        "name": "India Art, Architecture & Design Biennale",
        "base_url": "https://culture.gov.in/iaadb-2026",
        "authority_tier": "T0",
        "region": "india",
        "source_type": "official",
        "country": "IN",
        "enabled": True,
        "discovery_only": False,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    },
    {
        "source_id": "xhbt",
        "name": "XHBT Open Calls",
        "base_url": "https://www.xhbt.org/open-calls",
        "authority_tier": "T3",
        "region": "international",
        "source_type": "directory",
        "country": "INTL",
        "enabled": True,
        "discovery_only": True,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    },
    {
        "source_id": "opencall_ca",
        "name": "OPEN CALL — Art Grants",
        "base_url": "https://opencall.ca/",
        "authority_tier": "T3",
        "region": "international",
        "source_type": "directory",
        "country": "INTL",
        "enabled": True,
        "discovery_only": True,
        "fine_arts_fit": "HIGH",
        "crawl_depth": 2,
        "max_pages_per_source": 60
    }
]

with open("configs/sources.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

data.setdefault("sources", []).extend(new_sources)

with open("configs/sources.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, sort_keys=False)
