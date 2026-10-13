from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .page_gate import classify_page

def filter_seed_links(
    html: str,
    base_url: str,
    anchor_vocab: List[str],
    anchor_vocab_negative: List[str],
    seed_anchor_labels: Optional[List[str]] = None
) -> List[str]:
    """Extract and filter outbound links matching anchor vocabularies."""
    soup = BeautifulSoup(html, "lxml")
    target_labels = [label.lower() for label in (seed_anchor_labels or [])]
    vocab_pos = [v.lower() for v in anchor_vocab]
    vocab_neg = [v.lower() for v in anchor_vocab_negative]
    discovered_urls = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.scheme not in ("http", "https"):
            continue

        text = a.get_text(separator=" ", strip=True).lower()
        title_attr = (a.get("title") or "").lower()
        combined = f"{text} {title_attr}"

        # Check negative vocabulary
        if any(neg in combined for neg in vocab_neg) and not any(pos in combined for pos in vocab_pos):
            continue

        # Check positive match
        matches_custom = any(lbl in combined for lbl in target_labels)
        matches_vocab = any(pos in combined for pos in vocab_pos)

        if matches_custom or matches_vocab:
            discovered_urls.append(full_url)

    # Unique while preserving order
    seen = set()
    out = []
    for u in discovered_urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def expand_digest_page(html: str, url: str) -> List[Dict[str, Any]]:
    """Expand DIGEST page (e.g. Hyperallergic Opportunities in Month Year) into items."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Look for subheadings (h2, h3) or bold paragraphs followed by outbound links
    for heading in soup.find_all(["h2", "h3", "h4"]):
        title = heading.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        
        # Collect following sibling text and links until next heading
        para_texts = []
        links = []
        curr = heading.find_next_sibling()
        while curr and curr.name not in ["h2", "h3", "h4"]:
            if curr.name == "p":
                para_texts.append(curr.get_text(strip=True))
                for a in curr.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith("http"):
                        links.append((a.get_text(strip=True), href))
            curr = curr.find_next_sibling()

        body_text = " ".join(para_texts)
        if links:
            primary_label, primary_url = links[0]
            items.append({
                "title": title,
                "text": body_text,
                "outbound_url": primary_url,
                "digest_url": url,
                "resolved": False
            })

    return items

def expand_listing_page(html: str, url: str, detail_url_patterns: Optional[List[str]] = None) -> List[str]:
    """Expand LISTING page into detail opportunity links."""
    soup = BeautifulSoup(html, "lxml")
    detail_links = []
    
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href:
            continue
        full_url = urljoin(url, href)
        text = a.get_text(strip=True)
        kind = classify_page(url=full_url, title=text)
        if kind == "DETAIL":
            detail_links.append(full_url)
        elif detail_url_patterns:
            p = urlparse(full_url).path
            for pattern in detail_url_patterns:
                regex_pat = pattern.replace("{id}", r"\d+").replace("{slug}", r"[^/]+")
                if re.search(regex_pat, p):
                    detail_links.append(full_url)
                    break

    return list(dict.fromkeys(detail_links))

def generate_id_probes(pattern: str, seen_ids: List[int], window: int = 50) -> List[str]:
    """Generate URLs around seen IDs (seen ± window) for detail ID probing."""
    urls = []
    for sid in seen_ids:
        start_id = max(1, sid - window)
        end_id = sid + window
        for probe_id in range(start_id, end_id + 1):
            urls.append(pattern.replace("{id}", str(probe_id)))
    return list(dict.fromkeys(urls))
