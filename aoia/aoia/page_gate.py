"""Classify a fetched page BEFORE it can become an opportunity record.

Only DETAIL pages (and items expanded out of DIGEST/LISTING pages) may be stored as opportunities.
HOMEPAGE / LISTING / DIGEST pages are crawl seeds; NOT_FOUND pages are dropped.
"""
from __future__ import annotations
import re
from urllib.parse import urlparse

NOT_FOUND_RE = re.compile(r"\b(page not found|404|not found|file or directory not found|error 404)\b", re.I)
HOME_TITLE_RE = re.compile(r"^(home|homepage|welcome to|home\s*[-|–—])|[-|–—]\s*home\s*$|\bhomepage\b", re.I)
LISTING_PATH_RE = re.compile(
    r"/(notices?|noticeboard|latest|news|archive|archives|regions?|calls?|opportunit(?:y|ies)|"
    r"open-calls?|residenc(?:y|ies)|grants?|fellowships?|scholarships?|events?|exhibitions?)/?$", re.I)
LISTING_TITLE_RE = re.compile(r"\b(archive|latest|notices archive|all (?:calls|events|notices)|"
                              r"(?:india|southern asia|asia|europe|africa) \|)", re.I)
DIGEST_PATH_RE = re.compile(r"/opportunities-(?:in-)?[a-z]+-\d{4}(?:\.md)?/?$", re.I)
DETAIL_PATH_RE = re.compile(
    r"(event[_-]?details?/\d+|/(?:call|open-call|residency|fellowship|grant|scholarship|award|"
    r"competition|notice|noticeboard|opportunit(?:y|ies)|events?|exhibitions?)/[^/]+/?$)", re.I)
SIGNAL_RE = re.compile(r"\b(open call|call for (?:entries|applications|artists|proposals)|applications? (?:are )?(?:open|invited)|"
                       r"entries invited|apply (?:now|by|before)|last date|deadline|residency|fellowship|"
                       r"scholarship|grant|award|competition|submissions?)\b", re.I)
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]{3,9}\.?,?\s+\d{4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})\b")

def classify_page(url: str, title: str = "", status: int = 200, text: str = "") -> str:
    """Return NOT_FOUND | HOMEPAGE | DIGEST | LISTING | DETAIL | OTHER."""
    p = urlparse(url)
    path = p.path or "/"
    title = title or ""
    if status >= 400 or NOT_FOUND_RE.search(title):
        return "NOT_FOUND"
    if DIGEST_PATH_RE.search(path):
        return "DIGEST"
    if path in ("", "/", "/index.html", "/index.php", "/home") or HOME_TITLE_RE.search(title):
        return "HOMEPAGE"
    if DETAIL_PATH_RE.search(path) and not LISTING_PATH_RE.search(path):
        # detail only if the page itself shows opportunity signals or a date
        if SIGNAL_RE.search(title + " " + text[:3000]) or DATE_RE.search(text[:3000]):
            return "DETAIL"
        return "OTHER"
    if LISTING_PATH_RE.search(path) or LISTING_TITLE_RE.search(title):
        return "LISTING"
    if len(SIGNAL_RE.findall(text[:4000])) >= 2 and DATE_RE.search(text[:4000]):
        return "DETAIL"
    return "OTHER"

def may_become_record(kind: str) -> bool:
    return kind == "DETAIL"

def is_crawl_seed(kind: str) -> bool:
    return kind in ("HOMEPAGE", "LISTING", "DIGEST")