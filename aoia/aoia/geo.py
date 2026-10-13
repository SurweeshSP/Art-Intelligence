"""Deterministic geo classification. Never defaults to INTERNATIONAL just because data is missing."""
from __future__ import annotations
import re
from urllib.parse import urlparse

TLD_COUNTRY = {"in": "IN", "sg": "SG", "uk": "GB", "ae": "AE", "nl": "NL", "de": "DE", "fr": "FR", "ca": "CA",
               "jp": "JP", "kr": "KR", "au": "AU", "nz": "NZ", "es": "ES", "ch": "CH", "it": "IT", "se": "SE",
               "za": "ZA", "br": "BR", "hk": "HK", "my": "MY", "th": "TH", "lk": "LK", "np": "NP", "bd": "BD"}
ASIA = {"IN", "SG", "AE", "JP", "KR", "HK", "MY", "TH", "LK", "NP", "BD", "CN", "ID", "PH", "VN", "TW", "QA", "SA", "PK"}

CHENNAI = re.compile(r"\b(chennai|madras)\b", re.I)
TAMIL_NADU = re.compile(r"\b(tamil\s*nadu|coimbatore|madurai|puducherry|pondicherry|tiruchirappalli|trichy|salem)\b", re.I)
INDIA = re.compile(r"\b(india|indian|new delhi|delhi|mumbai|bengaluru|bangalore|kolkata|calcutta|hyderabad|pune|kochi|"
                   r"kerala|jaipur|ahmedabad|lucknow|bhubaneswar|odisha|garhi|agartala|tripura|goa|shillong|meghalaya|"
                   r"kasauli|baroda|vadodara|chandigarh|santiniketan|karnataka|maharashtra|gujarat|rajasthan)\b", re.I)
FOREIGN = {  # token -> ISO2
    "singapore": "SG", "london": "GB", "united kingdom": "GB", "uk": "GB", "england": "GB", "scotland": "GB",
    "paris": "FR", "france": "FR", "berlin": "DE", "germany": "DE", "stuttgart": "DE", "karlsruhe": "DE",
    "amsterdam": "NL", "netherlands": "NL", "new york": "US", "usa": "US", "united states": "US", "california": "US",
    "vermont": "US", "saratoga": "US", "peterborough": "US", "canada": "CA", "banff": "CA", "toronto": "CA",
    "sharjah": "AE", "dubai": "AE", "uae": "AE", "tokyo": "JP", "japan": "JP", "seoul": "KR", "korea": "KR",
    "australia": "AU", "sydney": "AU", "zurich": "CH", "switzerland": "CH", "spain": "ES", "madrid": "ES",
    "rome": "IT", "italy": "IT", "bangkok": "TH", "thailand": "TH", "colombo": "LK", "sri lanka": "LK",
    "kathmandu": "NP", "nepal": "NP", "dhaka": "BD", "bangladesh": "BD", "beijing": "CN", "china": "CN",
}
ONLINE = re.compile(r"\b(online|virtual|remote|worldwide|open to (?:all|artists worldwide)|international call)\b", re.I)

def _tld_country(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    parts = host.split(".")
    if len(parts) >= 2 and parts[-1] in TLD_COUNTRY:
        return TLD_COUNTRY[parts[-1]]
    if host.endswith(".gov.in") or host.endswith(".nic.in"):
        return "IN"
    return None

def _text_country(text: str) -> str | None:
    t = text or ""
    low = t.lower()
    best = None
    for tok, iso in FOREIGN.items():
        if re.search(rf"\b{re.escape(tok)}\b", low):
            best = iso
            break
    if CHENNAI.search(t) or TAMIL_NADU.search(t) or INDIA.search(t):
        # India wins only if no foreign location is named
        return best or "IN"
    return best

def resolve_geo(url: str, text: str = "", source_country: str | None = None, source_city: str | None = None,
                source_region: str | None = None, geo_basis: str = "registry") -> dict:
    """Return {geo_scope, country, basis}. basis is for logs/debug only (not shown in the UI).

    geo_basis="registry": organiser's own site -> fall back to registry country/city, then TLD.
    geo_basis="text":     directories / networks / news -> the SOURCE's country says nothing about where the
                          opportunity is, so only the item's own text counts (else UNKNOWN, never INTERNATIONAL).
    """
    text = text or ""
    t_country = _text_country(text)                     # 1. explicit location in the opportunity text
    if t_country == "IN":
        if CHENNAI.search(text):
            return {"geo_scope": "CHENNAI", "country": "IN", "basis": "text:chennai"}
        if TAMIL_NADU.search(text):
            return {"geo_scope": "TAMIL_NADU", "country": "IN", "basis": "text:tamil_nadu"}
        return {"geo_scope": "INDIA", "country": "IN", "basis": "text:india"}
    if t_country:
        return {"geo_scope": "ASIA" if t_country in ASIA else "INTERNATIONAL", "country": t_country, "basis": "text:foreign"}
    if geo_basis != "text":
        sc = (source_country or "").upper()             # 2. registry country / city
        if sc == "IN":
            if (source_city or "").lower() in ("chennai", "madras") or CHENNAI.search(urlparse(url).path):
                return {"geo_scope": "CHENNAI", "country": "IN", "basis": "registry:chennai"}
            return {"geo_scope": "INDIA", "country": "IN", "basis": "registry:IN"}
        if sc and sc not in ("GLOBAL", "EU"):
            return {"geo_scope": "ASIA" if sc in ASIA else "INTERNATIONAL", "country": sc, "basis": "registry:foreign"}
        tc = _tld_country(url)                          # 3. domain TLD
        if tc == "IN":
            return {"geo_scope": "INDIA", "country": "IN", "basis": "tld:in"}
        if tc:
            return {"geo_scope": "ASIA" if tc in ASIA else "INTERNATIONAL", "country": tc, "basis": "tld"}
        if sc in ("GLOBAL", "EU"):
            return {"geo_scope": "GLOBAL", "country": None, "basis": "registry:global"}
    if re.search(r"\b(online|virtual|remote)\b", text, re.I):   # 4. location independent
        return {"geo_scope": "ONLINE", "country": None, "basis": "text:online"}
    if re.search(r"\b(worldwide|open to (?:all|artists worldwide)|international call)\b", text, re.I):
        return {"geo_scope": "GLOBAL", "country": None, "basis": "text:global"}
    return {"geo_scope": "UNKNOWN", "country": None, "basis": "none"}