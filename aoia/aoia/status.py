from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from .models import Opportunity
from .priority import bucket

def compute_status(opp: Opportunity, now: Optional[datetime] = None) -> Opportunity:
    """Evaluate status based on IST now and deadline.
    
    Statuses:
      - OPEN: active future deadline
      - UPCOMING: opening date is in the future
      - ROLLING: rolling opportunity flag is True
      - DEADLINE_UNKNOWN: deadline is missing or 'UNKNOWN' (and not rolling)
      - RECENTLY_CLOSED: deadline passed <= 30 days ago
      - EXPIRED: deadline passed > 30 days ago
      
    Buckets:
      <24h FINAL HOURS, 0-3 CRITICAL, 4-7 URGENT, 8-14 VERY SOON, 15-30 PREPARE, 31-60 PLAN, 61+ WATCH.
    """
    if now is None:
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    
    if opp.rolling:
        opp.status = "ROLLING"
        opp.bucket_label = "ROLLING"
        opp.days_left = None
        return opp

    # Check upcoming
    if opp.opening_date and opp.opening_date != "UNKNOWN":
        try:
            op_dt = datetime.strptime(opp.opening_date, "%Y-%m-%d").date()
            if op_dt > now.date():
                opp.status = "UPCOMING"
                opp.bucket_label = "UPCOMING"
                opp.days_left = (op_dt - now.date()).days
                return opp
        except Exception:
            pass

    if not opp.deadline_date or opp.deadline_date == "UNKNOWN":
        opp.status = "DEADLINE_UNKNOWN"
        opp.bucket_label = "NO DEADLINE"
        opp.days_left = None
        return opp

    try:
        dl_dt = datetime.strptime(opp.deadline_date, "%Y-%m-%d").date()
        dl_days = (dl_dt - now.date()).days
        opp.days_left = dl_days

        if dl_days < 0:
            if dl_days >= -30:
                opp.status = "RECENTLY_CLOSED"
                opp.bucket_label = "CLOSED"
            else:
                opp.status = "EXPIRED"
                opp.bucket_label = "EXPIRED"
        else:
            opp.status = "OPEN"
            opp.bucket_label = bucket(dl_days)
    except Exception:
        opp.status = "DEADLINE_UNKNOWN"
        opp.bucket_label = "NO DEADLINE"
        opp.days_left = None

    return opp
