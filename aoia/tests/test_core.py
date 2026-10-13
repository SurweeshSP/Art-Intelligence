from aoia import detect, normalize, dedupe, status, scoring
from aoia.models import Opportunity

def test_homepage_not_opportunity():
    html = '''
    <html><head><title>Lalit Kala Akademi</title></head>
    <body>
    <nav>
      <a href="/">HOME</a>
      <a href="/about">ABOUT US</a>
      <a href="/regional">REGIONAL CENTRES</a>
      <a href="/exhibitions">EXHIBITIONS</a>
      <a href="/scholarship">RESEARCH & SCHOLARSHIP</a>
      <a href="/grants">GRANTS & FINANCIAL ASSISTANCE</a>
      <a href="/sale">NOW FOR SALE</a>
    </nav>
    <h1>National Exhibition of Art 2026</h1>
    </body></html>
    '''
    # url implies it's a generic page? Wait, no, detect doesn't parse menu, but has negative signals
    # detect uses `about`, `contact`, `gallery`, `sale`
    is_opp = detect.is_opportunity_page(html, "https://lalitkala.gov.in/")
    assert not is_opp

def test_event_details_no_deadline():
    o1 = Opportunity(
        id="1", title="Event Details", provider="test", type="exhibition", 
        location={"city": "Delhi"}, application_url="https://lalitkala.gov.in/event_details/339", 
        source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="UNKNOWN"
    )
    o1 = normalize.normalize_data(o1)
    o1 = status.compute_status(o1)
    assert o1.deadline_date == "UNKNOWN"
    assert o1.status == "DEADLINE_UNKNOWN"
    assert o1.geo_scope == "INDIA"

def test_geo_gazetteer():
    o1 = Opportunity(id="1", title="test", provider="test", type="test", location={"city": "Chennai"}, application_url="https://lalitkala.gov.in/regional", source={"url":"http", "tier":"T0", "discovered_via":"test"})
    assert normalize.normalize_data(o1).geo_scope == "CHENNAI"
    
    o2 = Opportunity(id="2", title="test", provider="test", type="test", location={"city": "Delhi"}, application_url="https://lalitkala.gov.in/", source={"url":"http", "tier":"T0", "discovered_via":"test"})
    assert normalize.normalize_data(o2).geo_scope == "INDIA"
    
    o3 = Opportunity(id="3", title="test", provider="test", type="test", location={"country": "SG"}, application_url="https://www.singaporeartmuseum.sg/", source={"url":"http", "tier":"T0", "discovered_via":"test"})
    assert normalize.normalize_data(o3).geo_scope == "INTERNATIONAL"

def test_deduplication():
    o1 = Opportunity(id="1", title="Lalit Kala", provider="LKA", type="open_call", location={"city": "test"}, application_url="https://lalitkala.gov.in/", canonical_url="https://lalitkala.gov.in/", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="UNKNOWN")
    o2 = Opportunity(id="2", title="Lalit Kala", provider="LKA", type="open_call", location={"city": "test"}, application_url="https://lalitkala.gov.in/event_details/339", canonical_url="https://lalitkala.gov.in/event_details/339", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="UNKNOWN")
    deduped = dedupe.deduplicate([o1, o2])
    assert len(deduped) == 1
    assert deduped[0].application_url == "https://lalitkala.gov.in/event_details/339"

def test_scoring_unknown_deadline():
    o1 = Opportunity(id="1", title="Unknown Deadline Opp", provider="LKA", type="open_call", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="UNKNOWN")
    o2 = Opportunity(id="2", title="Future Opp", provider="LKA", type="open_call", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="2026-11-30")
    ranked = scoring.score_and_rank([o1, o2], {}, {})
    assert ranked[0].id == "2"
    assert ranked[1].id == "1"
    assert ranked[1].priority_score <= 45.0
    assert ranked[0].priority_score > ranked[1].priority_score

def test_seed_records():
    o1 = Opportunity(id="1", title="Terrain", provider="Terrain", type="open_call", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="2026-09-12")
    o2 = Opportunity(id="2", title="SAM", provider="SAM", type="open_call", location={"city": "test"}, application_url="http", source={"url":"http", "tier":"T0", "discovered_via":"test"}, deadline_date="2026-09-30")
    o1 = status.compute_status(o1)
    o2 = status.compute_status(o2)
    assert o1.status == "RECENTLY_CLOSED"
    assert o2.status == "RECENTLY_CLOSED"
