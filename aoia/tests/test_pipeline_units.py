from datetime import datetime
from zoneinfo import ZoneInfo

from aoia import registry, geo, status, medium_filter, expansion, exports, unresolved
from aoia.models import Opportunity

def test_registry_v4_rules():
    # Valid registry loads without errors
    reg = registry.load_registry("configs/sources.yaml")
    assert len(reg.sources) == 142
    assert len(reg.unresolved_sources) == 17

    # Test failure cases
    bad_dict = {"sources": [{"source_id": "bad", "name": "bad"}]}
    errs = registry.validate_registry_dict(bad_dict)
    assert len(errs) > 0
    assert any("missing" in e for e in errs)

    # Test duplicate source_id
    dup_dict = {
        "sources": [
            {
                "source_id": "dup", "name": "A", "region": "india", "authority_tier": "T0",
                "base_url": "https://a.com", "source_type": "museum", "channel_role": "organiser",
                "fine_arts_fit": "HIGH", "geo_basis": "registry", "country": "IN", "enabled": True,
                "verification": "PENDING", "origin": "user_list", "crawl_interval_minutes": 720, "priority": 50
            },
            {
                "source_id": "dup", "name": "B", "region": "india", "authority_tier": "T0",
                "base_url": "https://b.com", "source_type": "museum", "channel_role": "organiser",
                "fine_arts_fit": "HIGH", "geo_basis": "registry", "country": "IN", "enabled": True,
                "verification": "PENDING", "origin": "user_list", "crawl_interval_minutes": 720, "priority": 50
            }
        ]
    }
    dup_errs = registry.validate_registry_dict(dup_dict)
    assert any("duplicate id" in e for e in dup_errs)

def test_unresolved_source_rules():
    assert unresolved.is_third_party_listing("https://en.wikipedia.org/wiki/Cholamandal")
    assert unresolved.is_third_party_listing("https://www.artisera.com/collections/art")
    assert unresolved.is_third_party_listing("https://timesofindia.indiatimes.com/city/chennai/art")
    assert not unresolved.is_third_party_listing("https://cholamandalartistvillage.org/")
    
    assert unresolved.token_match_in_domain_or_page("Cholamandal Artists' Village", "https://cholamandalartistvillage.org/", "Cholamandal Artists Village", "Official art village")

def test_medium_filter_rules():
    # Photography-only call dropped
    keep, inc, exc = medium_filter.filter_by_medium("Open call for contemporary photography and photobook entries")
    assert not keep
    assert "photography" in exc

    # Sculpture + photography kept
    keep2, inc2, exc2 = medium_filter.filter_by_medium("International residency for sculpture, installation, and photography artists")
    assert keep2
    assert "sculpture" in inc2 or "installation" in inc2

    # Ceramics kept
    keep3, inc3, exc3 = medium_filter.filter_by_medium("Fellowship for ceramics and textile art")
    assert keep3
    assert "ceramics" in inc3

def test_geo_basis_text_rules():
    # When geo_basis is text (directories/media), missing location yields UNKNOWN, never INTERNATIONAL
    res_unknown = geo.resolve_geo("https://artconnect.com/calls/1", text="Great artist residency open call", source_country="DE", geo_basis="text")
    assert res_unknown["geo_scope"] == "UNKNOWN"

    # Explicit Chennai in text
    res_chennai = geo.resolve_geo("https://artconnect.com/calls/2", text="Artist residency in Chennai, Tamil Nadu", source_country="DE", geo_basis="text")
    assert res_chennai["geo_scope"] == "CHENNAI"

    # Explicit Singapore in text
    res_sg = geo.resolve_geo("https://artconnect.com/calls/3", text="Exhibition call in Singapore", source_country="DE", geo_basis="text")
    assert res_sg["geo_scope"] == "ASIA"

    # When geo_basis is registry (organiser's own site), falls back to source country/city
    res_reg = geo.resolve_geo("https://lalitkala.gov.in/", text="", source_country="IN", source_city="Chennai", geo_basis="registry")
    assert res_reg["geo_scope"] == "CHENNAI"

def test_anchor_vocab_link_selection():
    html = """
    <html><body>
      <a href="/exhibitions">Exhibitions</a>
      <a href="/scholarship">Research & Scholarship</a>
      <a href="/about-us">About Us</a>
      <a href="/regional-chennai">Regional Centres > Chennai</a>
      <a href="/tender-notices">Tenders</a>
    </body></html>
    """
    vocab = ["open call", "exhibition", "scholarship"]
    vocab_neg = ["about", "tender"]
    seed_anchors = ["Regional Centres > Chennai"]
    links = expansion.filter_seed_links(html, "https://lalitkala.gov.in/", vocab, vocab_neg, seed_anchors)
    assert "https://lalitkala.gov.in/exhibitions" in links
    assert "https://lalitkala.gov.in/scholarship" in links
    assert "https://lalitkala.gov.in/regional-chennai" in links
    assert "https://lalitkala.gov.in/about-us" not in links
    assert "https://lalitkala.gov.in/tender-notices" not in links

def test_digest_expansion():
    html = """
    <html><body>
      <h2>International Painting Residency 2026</h2>
      <p>Studio and stipend provided. Apply at <a href="https://provider.org/apply">Official Page</a>.</p>
      <h2>Sculpture Commission Award</h2>
      <p>Outdoor installation prize. See <a href="https://sculpture-award.org/call">Commission Portal</a>.</p>
    </body></html>
    """
    items = expansion.expand_digest_page(html, "https://hyperallergic.com/opportunities-in-october-2026")
    assert len(items) == 2
    assert items[0]["title"] == "International Painting Residency 2026"
    assert items[0]["outbound_url"] == "https://provider.org/apply"

def test_id_probe_stop_rule():
    patterns = "/event_details/{id}"
    probes = expansion.generate_id_probes(patterns, [339], window=2)
    assert len(probes) == 5
    assert "/event_details/339" in probes
    assert "/event_details/337" in probes
    assert "/event_details/341" in probes

def test_status_boundaries():
    now = datetime(2026, 10, 12, tzinfo=ZoneInfo("Asia/Kolkata"))
    # Future deadline
    o_open = Opportunity(id="o1", title="A", provider="P", type="open call", application_url="http", deadline_date="2026-10-25")
    o_open = status.compute_status(o_open, now)
    assert o_open.status == "OPEN"
    assert o_open.bucket_label == "VERY SOON"
    assert o_open.days_left == 13

    # Recently closed (<= 30 days ago)
    o_closed = Opportunity(id="o2", title="B", provider="P", type="open call", application_url="http", deadline_date="2026-09-30")
    o_closed = status.compute_status(o_closed, now)
    assert o_closed.status == "RECENTLY_CLOSED"
    assert o_closed.bucket_label == "CLOSED"

    # Expired (> 30 days ago)
    o_exp = Opportunity(id="o3", title="C", provider="P", type="open call", application_url="http", deadline_date="2026-08-01")
    o_exp = status.compute_status(o_exp, now)
    assert o_exp.status == "EXPIRED"

    # No deadline
    o_none = Opportunity(id="o4", title="D", provider="P", type="open call", application_url="http", deadline_date="UNKNOWN")
    o_none = status.compute_status(o_none, now)
    assert o_none.status == "DEADLINE_UNKNOWN"
    assert o_none.bucket_label == "NO DEADLINE"

def test_export_formats():
    o = Opportunity(
        id="o1", title="Fine Arts Fellowship", provider="Kala Trust", type="fellowship",
        application_url="https://kala.org/apply", deadline_date="2026-11-15", geo_scope="INDIA"
    )
    csv_str = exports.export_to_csv([o])
    assert "Fine Arts Fellowship" in csv_str
    assert "Kala Trust" in csv_str

    md_str = exports.export_to_markdown([o])
    assert "| Fine Arts Fellowship |" in md_str

    json_str = exports.export_to_json([o])
    assert "Fine Arts Fellowship" in json_str

    ics_bytes = exports.export_to_ics([o])
    assert b"BEGIN:VCALENDAR" in ics_bytes
    assert b"Fine Arts Fellowship" in ics_bytes
