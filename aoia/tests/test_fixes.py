from aoia.page_gate import classify_page

# 13 real broken rows observed in real app output (§0 Acceptance Test)
ROWS = [
    {"title": "Home - MacDowell", "url": "https://www.macdowell.org/", "status": 200, "text": "Welcome to MacDowell artist residency fellowship"},
    {"title": "Notices Archive - India Art Fair", "url": "https://indiaartfair.in/noticeboard", "status": 200, "text": "Archive of notices and announcements"},
    {"title": "Page not found - India Art Fair", "url": "https://indiaartfair.in/noticeboard/<slug>", "status": 404, "text": "404 Page not found"},
    {"title": "India | On the Move", "url": "https://on-the-move.org/regions/india", "status": 200, "text": "Information resources on cultural mobility in India"},
    {"title": "Southern Asia | On the Move", "url": "https://on-the-move.org/regions/southern-asia", "status": 200, "text": "Mobility opportunities across Southern Asia region"},
    {"title": "Opportunities in October 2026", "url": "https://hyperallergic.com/opportunities-in-october-2026", "status": 200, "text": "Monthly digest of opportunities across art fields"},
    {"title": "Lalit Kala Akademi", "url": "https://lalitkala.gov.in/", "status": 200, "text": "National Academy of Art India official portal"},
    {"title": "Welcome to Singapore Art Museum (SAM)", "url": "https://www.singaporeartmuseum.sg/", "status": 200, "text": "Contemporary art in Southeast Asia"},
    {"title": "CPB Foundation Home | CPB Foundation", "url": "https://chennaiphotobiennale.foundation/", "status": 200, "text": "Chennai Photo Biennale foundation website"},
    {"title": "Chennai's Best Heritage Museum | Cultural Centre - Dakshinachitra", "url": "https://www.dakshinachitra.net/", "status": 200, "text": "Living history museum in Chennai"},
    {"title": "Serendipity | Serendipity Arts | Arts Festival", "url": "https://serendipityarts.org/", "status": 200, "text": "Interdisciplinary arts festival"},
    {"title": "Kochi Muziris Biennale - KMB", "url": "https://www.kochimuzirisbiennale.org/", "status": 200, "text": "International exhibition of contemporary art in Kochi"},
    {"title": "Latest - Charles Wallace India Trust", "url": "https://www.charleswallaceindiatrust.com/latest", "status": 200, "text": "Latest news and updates from CWIT"}
]

def test_acceptance_test_section_0_creates_zero_opportunity_records():
    """Acceptance test for §0: feeding the 13 pasted rows through the pipeline
    must create zero opportunity records because none of them are DETAIL pages.
    """
    created_records = []
    for row in ROWS:
        kind = classify_page(
            url=row["url"],
            title=row["title"],
            status=row["status"],
            text=row["text"]
        )
        # In the pipeline, only DETAIL pages may become opportunity records
        if kind == "DETAIL":
            created_records.append(row)
            
    assert len(created_records) == 0, f"Expected 0 opportunity records, got {len(created_records)}: {created_records}"

def test_page_gate_classifications():
    assert classify_page("https://www.macdowell.org/", "Home - MacDowell") == "HOMEPAGE"
    assert classify_page("https://indiaartfair.in/noticeboard", "Notices Archive - India Art Fair") == "LISTING"
    assert classify_page("https://indiaartfair.in/noticeboard/<slug>", "Page not found - India Art Fair", status=404) == "NOT_FOUND"
    assert classify_page("https://hyperallergic.com/opportunities-in-october-2026", "Opportunities in October 2026") == "DIGEST"
    assert classify_page("https://lalitkala.gov.in/event_details/339", "Open Call for 64th National Exhibition", status=200, text="Apply now before deadline 15th Nov 2026") == "DETAIL"
