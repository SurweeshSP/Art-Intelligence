from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urlparse
from .models import Opportunity

def normalize_title(title: str) -> str:
    """Normalize title by lowercasing and removing punctuation/whitespace noise."""
    t = re.sub(r"[^\w\s]", "", title.lower())
    return re.sub(r"\s+", " ", t).strip()

def normalize_url(url: str) -> str:
    """Canonicalize URL by stripping trailing slashes, fragments, and standard tracking query params."""
    p = urlparse(url)
    clean_path = p.path.rstrip("/") or "/"
    return f"{p.scheme}://{p.netloc.lower()}{clean_path}"

def deduplicate(opps: List[Opportunity]) -> List[Opportunity]:
    """Dedupe opportunities by canonical URL and normalized title + deadline.
    
    Uses hash map blocking (canonical_url and title+deadline) for O(N) performance.
    The more specific, higher-tier, or longer-detail page wins.
    """
    url_to_id: Dict[str, str] = {}
    title_dl_to_id: Dict[str, str] = {}
    id_to_opp: Dict[str, Opportunity] = {}

    for o in opps:
        canon_url = normalize_url(o.canonical_url or o.application_url)
        norm_t = normalize_title(o.title)
        dl = o.deadline_date or "UNKNOWN"
        td_key = f"{norm_t}|{dl}"

        existing_id = url_to_id.get(canon_url) or title_dl_to_id.get(td_key)

        if not existing_id or existing_id not in id_to_opp:
            # New unique record
            id_to_opp[o.id] = o
            url_to_id[canon_url] = o.id
            title_dl_to_id[td_key] = o.id
        else:
            existing = id_to_opp[existing_id]
            is_better = False
            if existing.deadline_date == "UNKNOWN" and o.deadline_date != "UNKNOWN":
                is_better = True
            elif len(o.application_url) > len(existing.application_url):
                is_better = True
            elif (o.source.tier or "T4") < (existing.source.tier or "T4"):
                is_better = True

            if is_better:
                # Replace existing record with better record
                del id_to_opp[existing_id]
                id_to_opp[o.id] = o
                url_to_id[canon_url] = o.id
                title_dl_to_id[td_key] = o.id
                # Update previous canonical url map to point to new id
                old_canon = normalize_url(existing.canonical_url or existing.application_url)
                url_to_id[old_canon] = o.id

    return list(id_to_opp.values())
