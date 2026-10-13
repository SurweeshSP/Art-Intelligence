from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from .models import Opportunity, Location, Financial, SourceData
from .geo import resolve_geo

DATE_PATTERNS = [
    # YYYY-MM-DD
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "%Y-%m-%d"),
    # DD.MM.YYYY
    (re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b"), "%d.%m.%Y"),
    # DD/MM/YYYY
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), "%d/%m/%Y"),
    # DD Month YYYY (e.g. 15th Dec 2026, 15 December 2026, upto 15th Dec 2026)
    (re.compile(r"\b(?:upto|by|before)?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\b", re.I), "MONTH_NAME"),
    # Month DD, YYYY
    (re.compile(r"\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", re.I), "MONTH_NAME_REV"),
]

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12
}

DEADLINE_CONTEXT_RE = re.compile(
    r"(?:deadline|last\s*date|apply\s*(?:by|before)|closing\s*date|entries\s*invited\s*(?:till|until|by|upto))\s*[:\-–—]?\s*([^\n\r<]{5,40})",
    re.I
)

TIME_RE = re.compile(r"\b(\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm|cet|ist|utc|gmt|est)?)\b", re.I)

TYPE_KEYWORDS = [
    ("residency", ["artist residency", "residency program", "residency"]),
    ("fellowship", ["fellowship program", "fellowship"]),
    ("grant", ["grant application", "research grant", "grant"]),
    ("scholarship", ["scholarship"]),
    ("award", ["award", "prize"]),
    ("open call", ["open call", "call for entries", "call for applications", "call for artists", "call for proposals"]),
    ("exhibition call", ["exhibition call", "exhibition"]),
    ("competition", ["competition"]),
    ("commission", ["public art commission", "commission"]),
]

NOISE_KEYWORDS = [
    "tender", "tenders", "recruitment", "vacancy", "vacancies", "rti",
    "annual report", "privacy policy", "terms of use", "tickets",
    "book tickets", "buy artwork", "shopping cart"
]

def is_noise_text(text: str) -> bool:
    """Detect if page is pure tender/recruitment/noise without call to action."""
    low = text.lower()
    noise_count = sum(1 for kw in NOISE_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", low))
    has_cta = bool(re.search(r"\b(apply|entries invited|submit|call for entries|call for applications|application)\b", low))
    return noise_count >= 2 and not has_cta

def parse_deadline(text: str) -> Tuple[Optional[str], Optional[str], Optional[str], str]:
    """Extract (deadline_date, deadline_time, deadline_timezone, snippet)."""
    # Look for deadline context first
    ctx_match = DEADLINE_CONTEXT_RE.search(text)
    target_texts = [ctx_match.group(0), ctx_match.group(1)] if ctx_match else []
    target_texts.append(text[:4000])

    for target in target_texts:
        for pat, fmt in DATE_PATTERNS:
            m = pat.search(target)
            if not m:
                continue
            try:
                if fmt == "%Y-%m-%d":
                    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", None, None, m.group(0)
                elif fmt in ("%d.%m.%Y", "%d/%m/%Y"):
                    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    return f"{y:04d}-{mo:02d}-{d:02d}", None, None, m.group(0)
                elif fmt == "MONTH_NAME":
                    d = int(m.group(1))
                    mo_str = m.group(2).lower()[:3]
                    mo = MONTH_MAP.get(mo_str)
                    y = int(m.group(3))
                    if mo:
                        return f"{y:04d}-{mo:02d}-{d:02d}", None, None, m.group(0)
                elif fmt == "MONTH_NAME_REV":
                    mo_str = m.group(1).lower()[:3]
                    d = int(m.group(2))
                    mo = MONTH_MAP.get(mo_str)
                    y = int(m.group(3))
                    if mo:
                        return f"{y:04d}-{mo:02d}-{d:02d}", None, None, m.group(0)
            except Exception:
                continue

    return None, None, None, ""

def extract_fee_and_funding(text: str) -> Financial:
    """Extract fee, stipend/grant, accommodation, travel, studio."""
    low = text.lower()
    fin = Financial()
    
    # Fee
    if re.search(r"\b(no application fee|free to apply|fee-free|no fee|entry is free)\b", low):
        fin.application_fee = 0.0
    elif m := re.search(r"(?:application\s*fee|entry\s*fee)\s*[:\-–—]?\s*(?:(?:inr|rs\.?|usd|\$|€|£)\s*)?(\d+)", low):
        try:
            fin.application_fee = float(m.group(1))
        except Exception:
            pass

    # Funding indicators
    grant_found = bool(re.search(r"\b(stipend|grant|honorarium|allowance|fellowship grant|prize)\b", low))
    acc_found = bool(re.search(r"\b(accommodation|housing|lodging|room and board|residential studio)\b", low))
    travel_found = bool(re.search(r"\b(travel grant|travel support|airfare|travel expenses covered)\b", low))
    studio_found = bool(re.search(r"\b(studio space|private studio|workspace provided|studio)\b", low))

    if grant_found:
        fin.grant_or_stipend = "PROVIDED"
    if acc_found:
        fin.accommodation = "PROVIDED"
    if travel_found:
        fin.travel = "PROVIDED"
    if studio_found:
        fin.studio = "PROVIDED"

    # Compute funding_level (0.0 to 1.0)
    score = 0.0
    if grant_found:
        score += 0.4
    if acc_found:
        score += 0.3
    if travel_found:
        score += 0.15
    if studio_found:
        score += 0.15
    fin.funding_level = min(1.0, score) if score > 0 else None

    return fin

def extract_opportunity_details(
    html: str,
    url: str,
    source_meta: Optional[Dict[str, Any]] = None
) -> Optional[Opportunity]:
    """Extract opportunity from HTML with source metadata and evidence tracking."""
    source_meta = source_meta or {}
    soup = BeautifulSoup(html, "lxml")
    
    # Clean text
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
        
    text = soup.get_text(separator=" ", strip=True)
    if is_noise_text(text):
        return None

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    if not title or len(title) < 5:
        h1 = soup.find("h1")
        if h1 and h1.text:
            title = h1.text.strip()
    if not title:
        title = source_meta.get("name", "Fine Arts Opportunity")

    # Clean title
    title = re.sub(r"\s+", " ", title)

    # Opportunity type
    low_text = (title + " " + text[:5000]).lower()
    opp_type = "open call"
    for cat, kws in TYPE_KEYWORDS:
        if any(kw in low_text for kw in kws):
            opp_type = cat
            break

    # Provider
    provider = source_meta.get("name")
    if not provider or provider == "Extracted Provider":
        provider = title.split(" - ")[0].split(" | ")[0].strip()
    if not provider:
        provider = "Official Organiser"

    # Deadline & Dates
    deadline_date, deadline_time, deadline_tz, dl_snippet = parse_deadline(text)
    rolling = bool(re.search(r"\b(rolling\s*(?:basis|deadline|submissions?)|apply\s*anytime)\b", low_text))

    # Evidence
    evidence = []
    if dl_snippet:
        evidence.append({
            "field": "deadline",
            "snippet": dl_snippet,
            "source_url": url,
            "confidence": 0.95
        })

    # Financials
    fin = extract_fee_and_funding(text)

    # Geo Resolution
    geo_res = resolve_geo(
        url=url,
        text=text[:5000],
        source_country=source_meta.get("country"),
        source_city=source_meta.get("city"),
        source_region=source_meta.get("region"),
        geo_basis=source_meta.get("geo_basis", "registry")
    )

    location = Location(
        city=source_meta.get("city"),
        country=geo_res.get("country") or source_meta.get("country"),
        state=source_meta.get("state")
    )

    tier = source_meta.get("authority_tier", "T0")
    channel_role = source_meta.get("channel_role", "organiser")

    # Verification level
    if tier == "T0" and deadline_date and channel_role == "organiser":
        verif = "CONFIRMED"
    elif source_meta.get("discovery_only"):
        verif = "UNVERIFIED"
    elif deadline_date:
        verif = "LIKELY"
    else:
        verif = "UNVERIFIED"

    opp_id = f"opp_{abs(hash(url))}"

    return Opportunity(
        id=opp_id,
        title=title,
        provider=provider,
        type=opp_type,
        deadline_date=deadline_date or "UNKNOWN",
        deadline_time=deadline_time,
        deadline_timezone=deadline_tz,
        rolling=rolling,
        location=location,
        geo_scope=geo_res.get("geo_scope", "UNKNOWN"),
        financial=fin,
        application_url=url,
        canonical_url=url,
        source=SourceData(
            url=source_meta.get("base_url", url),
            tier=tier,
            discovered_via=source_meta.get("origin", "CRAWL"),
            source_id=source_meta.get("source_id")
        ),
        evidence=evidence,
        verification=verif,
        career_stages=source_meta.get("career_level", ["any"]),
        status="OPEN" if deadline_date else "DEADLINE_UNKNOWN"
    )
