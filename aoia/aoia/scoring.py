from __future__ import annotations

from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import List, Optional
from .models import Opportunity
from .priority import priority, sort_key

def score_and_rank(
    opps: List[Opportunity],
    profile: Optional[dict] = None,
    weights: Optional[dict] = None
) -> List[Opportunity]:
    """Score and rank opportunities using priority.py rules.
    
    Fee-free first -> earliest deadline -> higher priority; unknown deadline sorts last.
    Unknown deadline priority is capped at 45.0. Non-opportunities (not DETAIL) are excluded.
    """
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    profile = profile or {}
    
    ranked_list: List[Opportunity] = []

    for opp in opps:
        # Determine deadline date object
        d_obj: Optional[date] = None
        if opp.deadline_date and opp.deadline_date != "UNKNOWN":
            try:
                d_obj = datetime.strptime(opp.deadline_date, "%Y-%m-%d").date()
                opp.days_left = (d_obj - now.date()).days
                if opp.days_left < 0:
                    opp.status = "RECENTLY_CLOSED"
                    opp.bucket_label = "CLOSED"
                elif opp.days_left <= 7:
                    opp.bucket_label = "ACT NOW"
                elif opp.days_left <= 14:
                    opp.bucket_label = "VERY SOON"
                elif opp.days_left <= 30:
                    opp.bucket_label = "PREPARE"
                else:
                    opp.bucket_label = "PLAN"
            except Exception:
                d_obj = None

        fee_val = opp.financial.application_fee
        funding_val = opp.financial.funding_level
        tier_val = opp.source.tier or "T0"
        verif_val = opp.verification or "UNVERIFIED"

        # Career level bonus
        fit_val = opp.fit_score
        profile_levels = profile.get("career_level", [])
        if any(lvl in opp.career_stages for lvl in profile_levels):
            fit_val = min(1.0, fit_val + 0.15)

        score = priority(
            page_kind="DETAIL",
            geo_scope=opp.geo_scope,
            deadline=d_obj,
            now=now,
            fee=fee_val,
            funding_level=funding_val,
            fit=fit_val,
            tier=tier_val,
            verification=verif_val,
            low_income=True
        )

        opp.priority_score = score if score is not None else 0.0

        # Construct why_text for detail panel
        days_str = f"{opp.days_left} days left" if opp.days_left is not None else "Deadline not stated"
        fee_str = "Fee-free" if fee_val == 0 else f"Fee: {fee_val}" if fee_val else "Fee unknown"
        opp.why_text = f"{days_str} · {opp.geo_scope} · {fee_str} · Trust {tier_val} ({verif_val})"

        ranked_list.append(opp)

    # Sort using sort_key: fee-free first -> earliest deadline -> higher priority -> unknown last
    def opp_sort_helper(o: Opportunity):
        rec = {
            "fee": o.financial.application_fee,
            "days_left": o.days_left if (o.days_left is not None and o.days_left >= 0) else None,
            "priority": o.priority_score
        }
        return sort_key(rec)

    ranked_list.sort(key=opp_sort_helper)
    return ranked_list
