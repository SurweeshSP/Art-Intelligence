import time
from aoia import scoring, dedupe
from aoia.models import Opportunity, Location, SourceData
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def test_scale_50k_opportunities():
    start = time.time()
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    opps = []
    
    # Generate 50,000 dummy opportunities
    for i in range(50000):
        opps.append(Opportunity(
            id=f"syn_opp_{i}",
            title=f"Synthetic {i}",
            provider="SynProvider",
            type="residency",
            location=Location(city="Chennai", country="IN"),
            geo_scope="CHENNAI",
            application_url=f"https://syn.com/{i}",
            source=SourceData(url=f"https://syn.com/{i}", tier="T0", discovered_via="SYNTHETIC"),
            deadline_date=(now + timedelta(days=i%100)).strftime("%Y-%m-%d"),
            status="OPEN"
        ))
        
    gen_time = time.time() - start
    
    start_dedupe = time.time()
    deduped = dedupe.deduplicate(opps)
    dedupe_time = time.time() - start_dedupe
    
    start_score = time.time()
    profile = {"max_application_fee_inr": 0}
    weights = {"geo": 0.3, "money": 0.25, "date": 0.3, "fit": 0.15}
    ranked = scoring.score_and_rank(deduped, profile, weights)
    score_time = time.time() - start_score
    
    assert len(ranked) == 50000
    
    # Assert performance boundaries (very generous for CI)
    assert dedupe_time < 2.0
    assert score_time < 5.0
    print(f"Scale test 50k opps - Gen: {gen_time:.2f}s, Dedupe: {dedupe_time:.2f}s, Score: {score_time:.2f}s")
