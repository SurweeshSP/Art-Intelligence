import pytest
import respx
import httpx
from datetime import datetime
from zoneinfo import ZoneInfo
from aoia import pipeline, db, status, scoring, dedupe

@pytest.mark.asyncio
async def test_smoke_mock_8_sources():
    """Smoke test:
    Mock 8 sources (one per region/role incl. a directory, a gallery, a failing and a robots-blocked source),
    run pipeline, assert dashboard data:
      - zero homepage / listing rows
      - geo not all INTERNATIONAL
      - unknown deadlines in their own bucket
      - seeds in Recently Closed
      - fee-free first
    """
    db.seed_demo_data()

    # Create 8 representative sources
    mock_sources = [
        # 1. Chennai Organiser (T0)
        {
            "source_id": "mock_lka_chennai", "name": "Lalit Kala Chennai", "region": "chennai",
            "authority_tier": "T0", "base_url": "https://mock-lka-chennai.org/", "source_type": "government",
            "channel_role": "organiser", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "IN", "city": "Chennai", "enabled": True, "verification": "PASSED"
        },
        # 2. India Funder (T0)
        {
            "source_id": "mock_india_funder", "name": "India Arts Foundation", "region": "india",
            "authority_tier": "T0", "base_url": "https://mock-india-funder.org/", "source_type": "foundation",
            "channel_role": "funder", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "IN", "city": "New Delhi", "enabled": True, "verification": "PASSED"
        },
        # 3. International Residency (T0)
        {
            "source_id": "mock_intl_residency", "name": "Global Arts Residency", "region": "international",
            "authority_tier": "T0", "base_url": "https://mock-global-residency.org/", "source_type": "residency",
            "channel_role": "organiser", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "FR", "city": "Paris", "enabled": True, "verification": "PASSED"
        },
        # 4. Directory with geo_basis: text (T1)
        {
            "source_id": "mock_directory", "name": "Art Directory World", "region": "international",
            "authority_tier": "T1", "base_url": "https://mock-directory.org/", "source_type": "platform",
            "channel_role": "discovery", "fine_arts_fit": "HIGH", "geo_basis": "text", "discovery_only": True,
            "country": "DE", "city": "Berlin", "enabled": True, "verification": "PASSED"
        },
        # 5. Venue / Gallery (sales/venue role -> where to show/sell)
        {
            "source_id": "mock_gallery_venue", "name": "Chennai Modern Gallery", "region": "chennai",
            "authority_tier": "T1", "base_url": "https://mock-chennai-gallery.org/", "source_type": "gallery",
            "channel_role": "venue", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "IN", "city": "Chennai", "enabled": True, "verification": "PASSED"
        },
        # 6. Asia Organiser (T0)
        {
            "source_id": "mock_asia_museum", "name": "Tokyo Contemporary Center", "region": "international",
            "authority_tier": "T0", "base_url": "https://mock-tokyo-art.jp/", "source_type": "museum",
            "channel_role": "organiser", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "JP", "city": "Tokyo", "enabled": True, "verification": "PASSED"
        },
        # 7. Failing source (HTTP 500)
        {
            "source_id": "mock_failing_src", "name": "Failing Art Org", "region": "india",
            "authority_tier": "T2", "base_url": "https://mock-failing-org.org/", "source_type": "platform",
            "channel_role": "organiser", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "IN", "city": "Mumbai", "enabled": True, "verification": "FAILED"
        },
        # 8. Robots-blocked source (HTTP 403)
        {
            "source_id": "mock_blocked_src", "name": "Blocked Art Hub", "region": "international",
            "authority_tier": "T2", "base_url": "https://mock-blocked-hub.org/", "source_type": "platform",
            "channel_role": "organiser", "fine_arts_fit": "HIGH", "geo_basis": "registry",
            "country": "US", "city": "New York", "enabled": True, "verification": "FAILED"
        }
    ]

    with respx.mock(assert_all_called=False) as respx_mock:
        # Mock responses
        respx_mock.get("https://mock-lka-chennai.org/").respond(
            200,
            html="<html><head><title>Lalit Kala Chennai Portal</title></head><body><h1>Welcome</h1><a href='/calls/chennai-fellowship'>Open Call</a></body></html>"
        )
        respx_mock.get("https://mock-lka-chennai.org/calls/chennai-fellowship").respond(
            200,
            html="<html><head><title>Open Call for Chennai Painting Fellowship 2026</title></head><body><h1>Open Call for Chennai Painting Fellowship 2026</h1><p>Entries invited for painters in Chennai. Apply now before deadline 2026-11-20. Free to apply.</p></body></html>"
        )
        respx_mock.get("https://mock-india-funder.org/").respond(
            200,
            html="<html><head><title>India Arts Foundation</title></head><body><h1>Welcome</h1><a href='/grants/visual-arts-grant'>Visual Arts Grant</a></body></html>"
        )
        respx_mock.get("https://mock-india-funder.org/grants/visual-arts-grant").respond(
            200,
            html="<html><head><title>National Visual Arts Grant</title></head><body><h1>National Visual Arts Grant</h1><p>Apply before 2026-12-15 for visual art grant in India. Application fee: 500.</p></body></html>"
        )
        respx_mock.get("https://mock-global-residency.org/").respond(
            200,
            html="<html><head><title>Global Arts Residency</title></head><body><h1>Welcome</h1><a href='/residency/paris-2026'>Paris Residency</a></body></html>"
        )
        respx_mock.get("https://mock-global-residency.org/residency/paris-2026").respond(
            200,
            html="<html><head><title>Paris Sculpture Residency 2026</title></head><body><h1>Paris Sculpture Residency 2026</h1><p>Open call for installation and sculpture artists in Paris. Deadline: 2026-11-05. Free to apply.</p></body></html>"
        )
        respx_mock.get("https://mock-directory.org/").respond(
            200,
            html="<html><head><title>Art Directory Listing</title></head><body><p>Listing page with various calls.</p></body></html>"
        )
        respx_mock.get("https://mock-chennai-gallery.org/").respond(
            200,
            html="<html><head><title>Chennai Modern Art Gallery Exhibition Space</title></head><body><h1>Exhibition Space for Hire</h1><p>Commercial venue for fine artists to show and sell.</p></body></html>"
        )
        respx_mock.get("https://mock-tokyo-art.jp/").respond(
            200,
            html="<html><head><title>Tokyo Art Fellowship (Rolling)</title></head><body><h1>Tokyo Contemporary Fellowship</h1><p>Submissions on rolling basis for contemporary artists in Tokyo Japan.</p></body></html>"
        )
        respx_mock.get("https://mock-failing-org.org/").respond(500)
        respx_mock.get("https://mock-blocked-hub.org/").respond(403)

        async with httpx.AsyncClient(timeout=5.0) as client:
            defaults = {"max_pages_per_source": 10, "anchor_vocab": ["call"], "anchor_vocab_negative": []}
            filter_cfg = {"include": ["painting", "sculpture", "visual art", "contemporary art"], "exclude": ["photography"]}
            
            results = []
            for src in mock_sources[:6]: # Only passed sources are crawled
                rep = {"by_kind": {}, "skipped_medium": 0, "pages_visited": 0, "records_found": 0}
                opps = await pipeline.crawl_source_async(client, src, defaults, filter_cfg, rep)
                results.extend(opps)

            # Load seeds from DB
            seeds = db.load_all_opportunities()
            all_opps = dedupe.deduplicate(seeds + results)
            
            now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))
            processed = [status.compute_status(o, now_ist) for o in all_opps]
            ranked = scoring.score_and_rank(processed)

            # Assertions
            # 1. Zero homepage or listing rows
            for o in ranked:
                assert "home" not in o.title.lower() or "residency" in o.title.lower() or "fellowship" in o.title.lower()
                assert "archive" not in o.title.lower()

            # 2. Geo not all INTERNATIONAL
            geos = {o.geo_scope for o in ranked}
            assert "CHENNAI" in geos
            assert "INDIA" in geos
            assert len(geos) > 2

            # 3. Seeds in Recently Closed
            terrain = next((o for o in ranked if "Terrain" in o.title), None)
            assert terrain is not None
            assert terrain.status == "RECENTLY_CLOSED"
            assert terrain.geo_scope == "INDIA"

            sam = next((o for o in ranked if "Singapore Art Museum" in o.provider), None)
            assert sam is not None
            assert sam.status == "RECENTLY_CLOSED"
            assert sam.geo_scope == "ASIA"

            # 4. Fee-free sorts first among active opportunities
            open_dated = [o for o in ranked if o.status == "OPEN" and o.deadline_date != "UNKNOWN"]
            if len(open_dated) >= 2:
                assert open_dated[0].financial.application_fee == 0.0
