# AOIA Pipeline Fixes (D1-D5)

## Defect Fixes

| Defect | Root Cause | Fix Applied | Test Name |
|---|---|---|---|
| **D1: Homepage stored as opportunity** | `is_opportunity_page` only counted matching keywords and allowed `sum >= 2` regardless of path. | Added path parsing; if the URL path is `/`, `""`, `/index.html`, etc., or matches a negative keyword (like `/about`), it returns `False`. Modified `extract.py` to extract a real noun for `type` instead of hardcoding `open_call`. | `test_homepage_not_opportunity` |
| **D2: Status OPEN with "999 days left"** | `status.py` defaulted `status="OPEN"` if `deadline_date` was missing, and `scoring.py` forced `days_left=999`. | Changed `status.py` to output `DEADLINE_UNKNOWN`. Dropped 999 days sentinel in `scoring.py`; missing deadlines now render as `n/a` or `Needs verification`. | `test_event_details_no_deadline` |
| **D3: Govt. of India labelled INTERNATIONAL** | `normalize.py` was hardcoded to check exactly "Chennai" or "Delhi". | Upgraded geo-scoping in `normalize.py`. Now deterministically checks `opp.location.city`, `opp.location.country` (e.g. `IN`), and finally the URL domain (`.in` -> `INDIA`, `.sg` -> `INTERNATIONAL`). | `test_geo_gazetteer` |
| **D4: Duplicate homepage + event details** | `dedupe.py` used `hash(url)` as the id, meaning identical content on different URLs created duplicates. | Changed deduplication logic to use a compound key: `f"{title}\|{deadline_date}"`. The record with the longer (more specific) URL wins. | `test_deduplication` |
| **D5: Score 0.52 for empty non-opportunity** | `scoring.py` blindly applied math even if essential fields were missing. | Added early exit to `score_and_rank`. If `title="Unknown"`, `type="UNKNOWN"`, or `deadline="UNKNOWN"`, the score is hard-capped at 0.1 and `why_text="Needs verification"`. | `test_scoring_unknown_deadline` |

## Measured Crawl Stats
(From offline fixture run)
- **Pages Visited**: 6 
- **Classified as Opportunities**: 2
- **Records Created/Updated**: 2
- **Errors**: 0
- **Duration**: 0.3s
