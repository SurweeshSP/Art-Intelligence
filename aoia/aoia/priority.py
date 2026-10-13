"""Priority (0-100). Unknown values never inflate or zero-out a score; non-opportunities are not ranked."""
from __future__ import annotations
from datetime import date, datetime
from typing import Optional

GEO = {"CHENNAI": 1.0, "TAMIL_NADU": 0.9, "INDIA": 0.8, "ASIA": 0.6, "INTERNATIONAL": 0.5,
       "GLOBAL": 0.55, "ONLINE": 0.55, "UNKNOWN": 0.3}
TRUST = {"T0": 1.0, "T1": 0.85, "T2": 0.7, "T3": 0.55, "T4": 0.4}
VERIF = {"CONFIRMED": 1.0, "LIKELY": 0.85, "UNVERIFIED": 0.6, "VERIFICATION_REQUIRED": 0.5}
W = {"geo": 0.30, "money": 0.25, "date": 0.30, "fit": 0.15}

def days_left(deadline: Optional[date], now: datetime) -> Optional[int]:
    if deadline is None:
        return None
    return (deadline - now.date()).days

def bucket(d: Optional[int]) -> str:
    if d is None:
        return "NO DEADLINE"
    if d < 0:
        return "CLOSED"
    if d < 1:
        return "FINAL HOURS"
    if d <= 3:
        return "CRITICAL"
    if d <= 7:
        return "URGENT"
    if d <= 14:
        return "VERY SOON"
    if d <= 30:
        return "PREPARE"
    if d <= 60:
        return "PLAN"
    return "WATCH"

def money_score(fee, funding_level) -> float:
    """fee: 0 -> free, None -> unknown, >0 -> paid. funding_level: 0..1 or None (unknown)."""
    fee_part = 1.0 if fee == 0 else 0.5 if fee is None else 0.0
    fund_part = 0.0 if funding_level is None else max(0.0, min(1.0, funding_level))
    return 0.4 * fee_part + 0.6 * fund_part

def priority(page_kind: str, geo_scope: str, deadline: Optional[date], now: datetime, fee=None,
             funding_level=None, fit: Optional[float] = None, tier: str = "T0",
             verification: str = "UNVERIFIED", low_income: bool = True) -> Optional[float]:
    if page_kind != "DETAIL":
        return None                                   # not an opportunity -> not ranked
    d = days_left(deadline, now)
    if d is not None and d < 0:
        return None                                   # closed -> separate list
    g = GEO.get(geo_scope, 0.3)
    m = money_score(fee, funding_level)
    ds = 0.25 if d is None else 1.0 if d < 1 else 1 - min(d, 90) / 90   # unknown deadline: low, fixed
    f = 0.5 if fit is None else fit
    wm = W["money"] * (1.25 if low_income else 1.0)
    base = (W["geo"] * g + wm * m + W["date"] * ds + W["fit"] * f) / (W["geo"] + wm + W["date"] + W["fit"])
    score = 100 * base * TRUST.get(tier, 0.4) * VERIF.get(verification, 0.5)
    if d is None:
        score = min(score, 45.0)                      # cap: a record without a deadline can't outrank dated ones
    return round(score, 1)

def sort_key(rec: dict):
    """Fee-free first -> earliest deadline -> higher priority. Unknown deadline sorts last."""
    fee_rank = 0 if rec.get("fee") == 0 else 1 if rec.get("fee") is None else 2
    dl = rec.get("days_left")
    return (fee_rank, dl is None, dl if dl is not None else 10**6, -(rec.get("priority") or 0))