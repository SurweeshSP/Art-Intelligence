# AOIA — Source Endpoints, Model Input & Execution Architecture

**Version:** 2.1 | **Date:** 09 October 2026 | **Region:** Chennai, Tamil Nadu, India
**Scope:** Web-only collection (API / feeds / sitemaps / HTML / search). No OCR, CSV or Excel ingestion.

---

## 0. Important notes before you build

1. **Your two seed records are already closed as of today (09 Oct 2026):**
   - Terrain (Delhi) — last date 12.09.2026 → `RECENTLY_CLOSED`
   - Singapore Art Museum Residency Cycle 4 — last date 30.09.2026 → `RECENTLY_CLOSED`
   They must appear under "Recently Closed", not "Open". Run the live crawl to fill the Open list.
2. **Source URLs below come from your AOIA architecture and have not been live-tested in this session.** Every source carries `verification: PENDING` until the health check in §3 passes. Do not publish an opportunity from a source with `PENDING` or `FAILED` status.
3. **"Authentic" rule:** *Search discovers. Official pages verify.* Directories (ArtConnect, ArtDeadline, etc.) are discovery only; the record must link back to the official provider URL (Tier T0) before it is marked `CONFIRMED`.
4. **"Income factor" is interpreted as the money dimension:** application fee (cost to the artist), funding (grant / stipend / prize / accommodation / travel), and the artist's `income_bracket` preference (e.g. low-income → fee-free and funded first). Change `income_policy` in §6 if you meant something else.

---

## 1. Execution flow

```text
Load artist profile + current time (IST)
  → select sources due for refresh (URL frontier)
  → fetch (API > feed > sitemap > static HTML > Playwright > search)
  → change detect (ETag / Last-Modified / content hash)
  → extract (JSON-LD → tables → regex/dateparser → small model for ambiguity)
  → normalize → validate → dedupe → canonical official URL check
  → store/version in PostgreSQL
  → status engine (OPEN / UPCOMING / RECENTLY_CLOSED / EXPIRED)
  → hard filter → score → sort → snapshot (Chennai / India / International)
```

---

## 2. Source registry — endpoints

Trust tiers: **T0** official provider/government · **T1** established network/directory · **T2** specialist publication · **T3** aggregator · **T4** unverified.
Method codes: `H` static HTML · `B` browser (Playwright) · `S` search discovery · `F` feed probe · `M` sitemap probe.

### 2.1 Chennai (priority 100, crawl every 3–6 h)

| source_id | Name | Endpoint | Tier | Method |
|---|---|---|---|---|
| cpb_foundation | Chennai Photo Biennale Foundation | https://chennaiphotobiennale.foundation/ | T0 | H, B, S |
| cpb_opencall | CPB Open Call | https://opencall.chennaiphotobiennale.com/ | T0 | H |
| lka_chennai | Lalit Kala Akademi (Regional Centre Chennai) | https://lalitkala.gov.in/ | T0 | H, S |
| kalakshetra | Kalakshetra Foundation | https://kalakshetra.in/ | T0 | H, S |
| dakshinachitra | DakshinaChitra | https://www.dakshinachitra.net/ | T0 | H, S |
| govt_museum_chennai | Government Museum Chennai | https://govtmuseumchennai.org/ | T0 | H, S |
| goethe_chennai | Goethe-Institut Chennai | https://www.goethe.de/ins/in/en/sta/che.html | T0 | H, S |
| iaf_noticeboard | India Art Fair Noticeboard | https://indiaartfair.in/noticeboard | T0 | H, S |

### 2.2 India (priority 90, crawl every 6–12 h)

| source_id | Name | Endpoint | Tier | Method |
|---|---|---|---|---|
| moc_india | Ministry of Culture | https://culture.gov.in/ | T0 | H, S |
| iccr | Indian Council for Cultural Relations | https://iccr.gov.in/ | T0 | H, S |
| lka_national | Lalit Kala Akademi | https://lalitkala.gov.in/ | T0 | H, S |
| sangeet_natak | Sangeet Natak Akademi | https://sangeetnatak.gov.in/ | T0 | H |
| sahitya_akademi | Sahitya Akademi | https://sahitya-akademi.gov.in/ | T0 | H |
| nsd | National School of Drama | https://nsd.gov.in/ | T0 | H |
| ngma | National Gallery of Modern Art | https://ngmaindia.gov.in/ | T0 | H |
| india_art_fair | India Art Fair | https://indiaartfair.in/ | T0 | H |
| khoj | KHOJ | https://khojstudios.org/ | T0 | H, S |
| serendipity | Serendipity Arts Foundation | https://serendipityarts.org/ | T0 | H, S |
| inlaks | Inlaks Shivdasani Foundation | https://www.inlaksfoundation.org/ | T0 | H |
| charles_wallace | Charles Wallace India Trust | https://www.charleswallaceindiatrust.com/ | T0 | H |
| british_council_in | British Council India | https://www.britishcouncil.in/ | T0 | H, S |
| goethe_india | Goethe-Institut India | https://www.goethe.de/ins/in/en/ | T0 | H, S |
| terrain | Terrain (seed from ART DATA) | https://www.terrain.art/ | T0 | H |

### 2.3 International (priority 80, crawl every 6–24 h)

| source_id | Name | Endpoint | Tier | Method |
|---|---|---|---|---|
| artconnect | ArtConnect | https://www.artconnect.com/ | T1 | H, S, M |
| transartists | TransArtists | https://www.transartists.org/ | T1 | H, S |
| on_the_move | On the Move | https://on-the-move.org/ | T1 | H, F, S |
| asef_culture360 | ASEF Culture360 | https://culture360.asef.org/ | T1 | H, S |
| aca | Artist Communities Alliance | https://artistcommunities.org/ | T1 | H, S |
| res_artis | Res Artis | https://resartis.org/ | T1 | H, S |
| residency_unlimited | Residency Unlimited | https://residencyunlimited.org/ | T1 | H, S |
| artdeadline | ArtDeadline.com | https://artdeadline.com/ | T2 | H, S |
| artjobs | Art Jobs | https://www.artjobs.org/ | T2 | H, S |
| artrabbit | ArtRabbit | https://www.artrabbit.com/ | T2 | H, S |
| eflux | e-flux | https://www.e-flux.com/ | T2 | H, F, S |
| rhizome | Rhizome | https://rhizome.org/ | T2 | H, F, S |
| culture_moves_europe | Culture Moves Europe (EU) | https://culture.ec.europa.eu/ | T0 | H, S |
| artists_at_risk | Artists at Risk | https://artistsatrisk.org/ | T1 | H, S |
| artconnect_mag | ArtConnect Magazine | https://www.magazine.artconnect.com/ | T2 | H, S |
| sam_singapore | Singapore Art Museum (seed from ART DATA) | https://www.singaporeartmuseum.sg/ | T0 | H |

### 2.4 Auto-probe paths (run per domain, record only if HTTP 200)

```text
/robots.txt        → read Sitemap: lines + crawl rules
/sitemap.xml       /sitemap_index.xml
/feed  /rss  /rss.xml  /feed.xml  /atom.xml
/open-calls  /opportunities  /residencies  /apply  /noticeboard  /news
```
Feed and sitemap URLs are stored only after a successful probe — never guessed into the registry.

### 2.5 Search discovery endpoints

Use a configurable web-search API. Query families (vary by geo, year, month):

```text
Chennai artist open call | Chennai artist residency | Chennai art fellowship
India artist open call 2026 | India artist residency | India visual arts grant
international artist residency open call | fully funded artist residency
artist grant no application fee | "applications open" artist residency 2026
site:.gov.in artist fellowship | site:goethe.de artist open call India
site:britishcouncil.in artist opportunity | site:.edu artist residency open call
```

### 2.6 Registry record format

```yaml
source_id: cpb_opencall
name: CPB Open Call
region: chennai
source_type: official_provider
authority_tier: T0
base_url: https://opencall.chennaiphotobiennale.com/
collection: {api: false, rss: false, html: true, browser: false, search: true, sitemap: false}
priority: 100
crawl_interval_minutes: 180
canonical_verification: source_is_canonical
verification: PENDING        # PENDING | PASSED | FAILED
last_health_check: null
```

---

## 3. Source authenticity gate (must pass before use)

| # | Check | Pass condition |
|---|---|---|
| 1 | Reachability | HTTP 200 (follow ≤3 redirects), TLS valid |
| 2 | Identity | Domain matches the organization (gov.in / .org / known institute domain) |
| 3 | robots.txt / ToS | Path allowed; no login/paywall/CAPTCHA |
| 4 | Opportunity signal | Page contains ≥2 of: open call, apply, deadline, residency, fellowship, grant, scholarship |
| 5 | Canonical link | Directory records resolve to an official URL; otherwise `UNVERIFIED` |
| 6 | Freshness | Page shows a date or deadline within the last 12 months |

Record status: `CONFIRMED` (T0 + explicit deadline + apply link) · `LIKELY` · `UNVERIFIED` · `EXPIRED` · `CLOSED` · `REMOVED`.
Missing facts are stored as `UNKNOWN`, never guessed.

---

## 4. Opportunity record (extracted from the web)

```json
{
  "id": "opp_000001",
  "title": "Cycle 4 Residency",
  "provider": "Singapore Art Museum",
  "type": "residency",
  "duration": "1-3 months",
  "announcement_date": "2026-07-12",
  "opening_date": "2026-07-12",
  "deadline_date": "2026-09-30",
  "deadline_time": null,
  "deadline_timezone": null,
  "location": {"city": "Singapore", "country": "SG"},
  "geo_scope": "INTERNATIONAL",
  "eligibility_geography": ["UNKNOWN"],
  "age_min": 18,
  "financial": {
    "application_fee": 0,
    "currency": null,
    "grant_or_stipend": "UNKNOWN",
    "accommodation": "UNKNOWN",
    "travel": "UNKNOWN",
    "studio": "UNKNOWN"
  },
  "requirements": ["UNKNOWN"],
  "application_url": "https://www.singaporeartmuseum.sg/",
  "source": {"url": "https://www.singaporeartmuseum.sg/", "tier": "T0", "discovered_via": "SEED"},
  "evidence": [{"field": "deadline", "snippet": "…", "url": "…", "confidence": 0.0}],
  "status": "RECENTLY_CLOSED",
  "verification": "UNVERIFIED",
  "first_seen": null, "last_verified": null
}
```

Seed records from your ART DATA sheet (to be re-verified on the official pages):

| Title | Type | Announced | Last date | Place | Fee | Age | Status today |
|---|---|---|---|---|---|---|---|
| Terrain — online work submission | Open call | 03.07.2026 | 12.09.2026 | Delhi, India | None | Above 21 | RECENTLY_CLOSED |
| Singapore Art Museum — Cycle 4 Residency (1–3 mo) | Residency | 12.07.2026 | 30.09.2026 | Singapore | None | Above 18 | RECENTLY_CLOSED |

---

## 5. Model input

### 5.1 Artist input (`artist_profile.json`)

```json
{
  "location": {"city": "Chennai", "state": "Tamil Nadu", "country": "IN"},
  "nationality": "IN",
  "age": null,
  "career_stage": "emerging",
  "mediums": ["installation", "sculpture", "mixed_media"],
  "themes": ["technology", "human perception", "identity", "space"],
  "income_bracket": "low",
  "income_policy": "prefer_fee_free_and_funded",
  "max_application_fee_inr": 0,
  "opportunity_types": ["residency", "fellowship", "open_call", "grant", "exhibition"],
  "preferred_regions": ["chennai", "india", "asia", "europe", "global"],
  "travel_ok": true,
  "weights": {"geo": 0.30, "money": 0.25, "date": 0.30, "fit": 0.15}
}
```
`age`, `nationality` and `income_bracket` are required for eligibility — fill them in; unknown values give `POSSIBLY_ELIGIBLE`, not `ELIGIBLE`.

### 5.2 Run input (`run_config.json`)

```json
{
  "now": "2026-10-09T09:48:00+05:30",
  "timezone": "Asia/Kolkata",
  "recently_closed_days": 30,
  "recently_opened_days": 30,
  "closing_soon_days": [3, 7, 14, 30, 60],
  "regions": ["chennai", "india", "international"],
  "top_n": 50
}
```

---

## 6. Ranking logic (geo → money → date)

**Step 1 — Status:** `now` is compared to opening/deadline in the opportunity's own timezone. Only `OPEN` (and `UPCOMING` in a separate list) enter the ranked list.

**Step 2 — Hard filters (deterministic):** deadline not passed · fee ≤ `max_application_fee_inr` · age/nationality/residency/medium eligibility not `NOT_ELIGIBLE`.

**Step 3 — Sub-scores (0–1):**

```text
geo_score:   CHENNAI/TAMIL_NADU = 1.0 | INDIA = 0.8 | ASIA = 0.6 | INTERNATIONAL/GLOBAL/ONLINE = 0.5
             (opportunity location AND eligibility_geography must both allow the artist)

money_score: 0.40 * fee_free (1 if fee==0, else 0)
           + 0.60 * funding_level
             funding_level: fully funded (stipend + accommodation + travel) = 1.0
                            partial funding = 0.5 | none/UNKNOWN = 0.0
             (income_bracket=low multiplies money_score weight ×1.25)

date_score:  1 - min(days_to_deadline, 90) / 90       # closer deadline = higher
             days_to_deadline < 1 day → 1.0 (FINAL HOURS)

fit_score:   cosine(artist_embedding, opportunity_embedding)   # BAAI/bge-small-en-v1.5
```

**Step 4 — Priority:**

```text
PRIORITY = (w_geo*geo + w_money*money + w_date*date + w_fit*fit)
           × eligibility_confidence × source_trust(T0=1.0 … T4=0.4)
```

**Step 5 — Tie-break sort (matches your sheet's rule):**
1. fee = none first → 2. earliest last date → 3. time required for submission (low effort first) → 4. higher PRIORITY.

**Deadline buckets:** 0–3 d CRITICAL · 4–7 URGENT · 8–14 VERY SOON · 15–30 PREPARE · 31–60 PLAN · 61+ WATCH · <24 h FINAL HOURS.

---

## 7. Output (per run)

```text
outputs/latest.json | latest.md | latest.csv | snapshots/<timestamp>.json
Lists: CHENNAI · INDIA · INTERNATIONAL · Closing today/3/7/14/30 d · New · Recently closed
       No fee · Fully funded · High match · Deadline changed · Verification required
```

Each row: title, provider, geo_scope, deadline + days left, fee, funding, match %, priority bucket, official link, verification status, evidence URL.

---

## 8. Build order for today

1. Create `configs/sources/*.yaml` from §2 with `verification: PENDING`.
2. Run the §3 health check; keep only `PASSED` sources.
3. Implement fetch → extract (`dateparser`, regex, JSON-LD) → store (PostgreSQL).
4. Implement status + hard filters + scoring from §6.
5. Seed the two ART DATA records, confirm they show as `RECENTLY_CLOSED`.
6. Produce `latest.md` and review manually for the first run (human-in-the-loop for low confidence).

## 9. Compliance

Respect robots.txt, ToS, rate limits (≥2 s per domain), no login/CAPTCHA/paywall bypass, store facts + source URL rather than full page copies, treat page text as untrusted (never as instructions).
