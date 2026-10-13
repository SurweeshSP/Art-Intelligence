import os

def rewrite(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

rewrite("aoia/detect.py", """\
def is_opportunity_page(html: str, url: str = "") -> bool:
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    if parsed.path in ["", "/", "/index.html", "/home"] and not parsed.query:
        return False
        
    signals = ["apply", "call", "residency", "fellowship", "scholarship", "grant", "award", "competition", "submission", "exhibition", "notice", "event_details", "circular"]
    neg_signals = ["about", "contact", "gallery", "library", "publication", "login", "admin", "sitemap", "tender", "recruitment", "rti", "sale", "shop", "donate"]
    text = html.lower()
    url_lower = url.lower()
    
    # If the URL path implies it's a generic page
    for neg in neg_signals:
        if "/" + neg in url_lower or neg + ".htm" in url_lower:
            return False
            
    pos_count = sum(1 for s in signals if s in text)
    if pos_count >= 2:
        return True
    return False
""")

rewrite("aoia/dedupe.py", """\
def deduplicate(opps: list) -> list:
    seen = {}
    for o in opps:
        # Dedupe by normalised title + deadline to merge homepage and detail page
        key = f"{o.title.lower().strip()}|{o.deadline_date}"
        if key not in seen:
            seen[key] = o
        else:
            # If the new one has a longer URL, it might be the specific page
            if len(o.application_url) > len(seen[key].application_url):
                seen[key] = o
    return list(seen.values())
""")
