# Art Opportunity Intelligence Agent (AOIA)

## Final Architecture --- Real-Time Art Opportunity Discovery, Ranking & Deadline Intelligence

**Version:** 2.0\
**Date:** October 2026\
**Status:** Final Architecture / Implementation Blueprint\
**Primary Region:** Chennai, Tamil Nadu, India\
**Coverage:** Chennai → India → International\
**Primary Goal:** Every time the system runs, produce a fresh, verified,
deduplicated and prioritized list of currently available art
opportunities.

------------------------------------------------------------------------

# 1. Executive Summary

The **Art Opportunity Intelligence Agent (AOIA)** is an automated
intelligence system for continuously discovering and organizing
opportunities for artists.

The system is designed around a simple operational requirement:

> **Whenever AOIA runs, it should tell the artist what opportunities are
> available right now, what is closing soon, what has recently opened,
> what has already closed, and what is coming next.**

The system is not merely an opportunity database.

It is a **real-time opportunity intelligence pipeline**.

The system continuously collects information from permitted public
sources and converts it into a normalized opportunity dataset
containing:

-   exhibitions
-   open calls
-   residencies
-   fellowships
-   scholarships
-   grants
-   competitions
-   awards
-   art fairs
-   biennales
-   commissions
-   workshops
-   research opportunities
-   institutional programmes
-   artist development programmes

The system prioritizes opportunities by:

1.  Current availability
2.  Deadline
3.  Geographic relevance
4.  Artist eligibility
5.  Practice/medium relevance
6.  Funding
7.  Application cost
8.  Opportunity quality
9.  Application effort
10. Source confidence

------------------------------------------------------------------------

# 2. Core Runtime Requirement

Every execution of the system should produce a current opportunity
intelligence snapshot.

``` text
AOIA RUN
   |
   +--> Current Date/Time
   |
   +--> Refresh Sources
   |
   +--> Discover New Opportunities
   |
   +--> Update Existing Opportunities
   |
   +--> Remove/Mark Expired Opportunities
   |
   +--> Verify Deadlines
   |
   +--> Deduplicate
   |
   +--> Match Artist
   |
   +--> Rank
   |
   +--> Generate Lists
   |
   +--> Generate Report
   |
   +--> Store Snapshot
```

The output should never be treated as permanent truth.

Every run creates a new **Opportunity Snapshot**.

------------------------------------------------------------------------

# 3. Geographic Intelligence

The system must maintain three primary geographic views.

``` text
ART OPPORTUNITIES
|
+-- CHENNAI
|   +-- Chennai
|   +-- Tamil Nadu
|   +-- Chennai-based institutions
|
+-- INDIA
|   +-- All Indian states
|   +-- National programmes
|   +-- India-based institutions
|
+-- INTERNATIONAL
    +-- Asia
    +-- Europe
    +-- North America
    +-- South America
    +-- Africa
    +-- Middle East
    +-- Oceania
    +-- Global / location-independent
```

Geographic relevance is not the same as event location.

For example:

``` text
Opportunity Location:
London

Eligibility:
International artists

Artist Location:
Chennai

Result:
INTERNATIONAL + ELIGIBLE
```

Therefore the system maintains both:

``` text
opportunity_location
eligibility_geography
```

------------------------------------------------------------------------

# 4. Temporal Opportunity Views

The system must generate multiple time-oriented lists on every run.

## 4.1 Newly Opened

Opportunities whose application window has recently opened.

``` text
OPENED_RECENTLY
```

Default:

``` text
announcement/open date <= 30 days
```

The window must be configurable.

------------------------------------------------------------------------

## 4.2 Currently Open

Opportunities for which:

``` text
now < deadline
```

and:

``` text
status = OPEN
```

------------------------------------------------------------------------

## 4.3 Closing Soon

Opportunities approaching their deadline.

Default buckets:

``` text
0–3 days       CRITICAL
4–7 days       URGENT
8–14 days      VERY SOON
15–30 days     PREPARE
31–60 days     PLAN
61+ days       WATCH
```

------------------------------------------------------------------------

## 4.4 Recently Closed

Opportunities that closed recently.

Default:

``` text
deadline < now
AND
deadline >= now - 30 days
```

These are useful for historical analysis and recurrence detection.

------------------------------------------------------------------------

## 4.5 Upcoming / Expected

Historical recurring opportunities that are expected to open in the
future.

Example:

``` text
2024 → October
2025 → October
2026 → September
```

Output:

``` text
EXPECTED NEXT CYCLE
Confidence: Medium
```

The system must never represent a predicted opportunity as a confirmed
open call.

------------------------------------------------------------------------

# 5. Final Runtime Output

Every execution should generate the following structure.

``` text
============================================================
ART OPPORTUNITY INTELLIGENCE — CURRENT SNAPSHOT
============================================================

Run Time:
04 October 2026, 09:30 IST

Sources Checked:
127

Sources Changed:
31

New Opportunities:
42

Updated Opportunities:
18

Expired Opportunities:
11

Duplicates Removed:
27

============================================================

CHENNAI
============================================================

New:
8

Open:
21

Closing Soon:
6

Recently Closed:
4

============================================================

INDIA
============================================================

New:
19

Open:
74

Closing Soon:
18

Recently Closed:
13

============================================================

INTERNATIONAL
============================================================

New:
15

Open:
183

Closing Soon:
42

Recently Closed:
31

============================================================

TOP ACTIONABLE OPPORTUNITIES
============================================================

1. Opportunity A
   Match: 96%
   Location: Chennai
   Deadline: 7 days
   Fee: None
   Priority: CRITICAL

2. Opportunity B
   Match: 93%
   Location: India
   Deadline: 14 days
   Fee: None
   Priority: VERY SOON

3. Opportunity C
   Match: 91%
   Location: International
   Deadline: 28 days
   Fee: None
   Priority: PREPARE
```

------------------------------------------------------------------------

# 6. System Architecture

``` text
                         INTERNET
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
   Websites              RSS/Feeds             APIs
       |                    |                    |
       +--------------------+--------------------+
                            |
                            v
                  +----------------------+
                  | SOURCE DISCOVERY     |
                  | & SOURCE REGISTRY    |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | COLLECTION ENGINE    |
                  | HTTP / Playwright     |
                  | HTML / PDF / RSS     |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | CHANGE DETECTOR      |
                  | Hash / ETag / Finger |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | OPPORTUNITY DETECTOR |
                  | Rules + Small Model  |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | EXTRACTION ENGINE    |
                  | Rules + NLP + LLM    |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | NORMALIZATION        |
                  | Dates / Location     |
                  | Fees / Eligibility   |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | VALIDATION ENGINE    |
                  | Confidence / Rules   |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | DEDUPLICATION       |
                  | Entity Resolution   |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | POSTGRESQL           |
                  | + PGVECTOR           |
                  +----------+-----------+
                             |
             +---------------+----------------+
             |                                |
             v                                v
   +--------------------+           +--------------------+
   | ARTIST MATCHING    |           | TEMPORAL ENGINE    |
   | Rules + Embeddings |           | Deadline + Status  |
   +---------+----------+           +---------+----------+
             |                                |
             +---------------+----------------+
                             |
                             v
                  +----------------------+
                  | RANKING ENGINE       |
                  +----------+-----------+
                             |
                             v
                  +----------------------+
                  | REPORT GENERATOR     |
                  +----------+-----------+
                             |
             +---------------+----------------+
             |               |                |
             v               v                v
        Dashboard          JSON/CSV       Notifications
                                         Email / Telegram
                                         Discord / Push
```

------------------------------------------------------------------------

# 7. Source Architecture

The source registry is the heart of the discovery system.

Each source must have:

``` json
{
  "source_id": "source_001",
  "name": "Example Institution",
  "url": "https://example.org",
  "country": "IN",
  "region": "Tamil Nadu",
  "city": "Chennai",
  "source_type": "official",
  "categories": [
    "residency",
    "exhibition",
    "fellowship"
  ],
  "crawl_method": "html",
  "crawl_frequency": "daily",
  "trust_score": 1.0,
  "active": true
}
```

------------------------------------------------------------------------

# 8. Source Trust Hierarchy

``` text
TIER 1
Official opportunity provider
        |
        v
TIER 2
Government / university / institutional partner
        |
        v
TIER 3
Established opportunity directory
        |
        v
TIER 4
Community / newsletter / announcement
        |
        v
TIER 5
Unverified third-party source
```

The system should always prefer the authoritative source when duplicates
exist.

------------------------------------------------------------------------

# 9. Data Collection Strategy

AOIA is an **internet-native opportunity intelligence system**. Its collection layer is intentionally restricted to information that can be obtained from live internet sources through APIs, web search, web pages, feeds, structured web data, and browser-based web extraction.

## 9.1 Collection Principle

The system should behave like a continuously running web intelligence crawler rather than a document-analysis system.

```text
Internet
   |
   +--> Official APIs
   |
   +--> Public JSON / GraphQL / REST endpoints
   |
   +--> RSS / Atom / XML feeds
   |
   +--> Static HTML pages
   |
   +--> Embedded JSON / JSON-LD / schema.org
   |
   +--> JavaScript-rendered web pages
   |
   +--> Search engines / web search
   |
   +--> Public opportunity directories
   |
   +--> Official institutional announcement pages
   |
   +--> Public newsletters / announcement web pages
   |
   +--> Public social/web announcement pages where permitted
   |
   v
AOIA Collection Fabric
   |
   v
Normalization -> Verification -> Deduplication -> Status -> Matching -> Ranking
```

### Explicitly excluded from the core collection architecture

AOIA does **not** depend on:

- OCR pipelines
- image-to-text extraction
- scanned-document processing
- local CSV datasets
- local Excel spreadsheets
- manually maintained opportunity spreadsheets
- offline document folders
- PDF-to-text as a primary collection mechanism

A web page may contain a link to a PDF, but the PDF is treated only as a **discovered reference/application link** unless a future implementation explicitly adds a document-ingestion module. The core AOIA collector does not require OCR or local document ingestion.

---

# 9A. What AOIA Collects From the Internet

Every discovered opportunity should be converted into a normalized web record.

## Opportunity identity

- opportunity title
- organization/provider
- opportunity type
- opportunity category
- source URL
- canonical opportunity URL
- application URL
- source domain
- source type
- source authority

## Timing

- announcement date
- application opening date
- application deadline
- timezone of deadline
- rolling/ongoing flag
- expected recurrence
- programme period
- last-seen timestamp
- first-seen timestamp
- last-changed timestamp

## Geography

- provider country
- provider city
- opportunity location
- Chennai relevance
- India relevance
- international eligibility
- remote/online availability
- eligible countries
- excluded countries

## Artist eligibility

- age requirement
- career stage
- nationality requirement
- residency requirement
- discipline
- medium
- thematic requirement
- professional experience
- education requirement
- portfolio requirement
- publication/exhibition requirement
- language requirement
- institutional affiliation requirement

## Financial information

- application fee
- participation fee
- grant amount
- stipend
- prize
- production support
- travel support
- accommodation
- studio support
- material support
- insurance/support where stated

## Application information

- application method
- form URL
- application platform
- required materials
- portfolio requirements
- proposal requirements
- CV requirements
- statement requirements
- references
- selection process
- selection date
- notification date

## Evidence and provenance

- exact source URL
- source page title
- source domain
- extraction timestamp
- evidence snippets
- field-level confidence
- source authority score
- verification status
- canonical provider URL
- discovered-through URL

---

# 9B. Internet Source Classes

AOIA should collect from several complementary source classes instead of relying on one opportunity website.

| Source class | Examples | Collection method | Priority |
|---|---|---|---|
| Official government | Ministry of Culture, ICCR | HTML/API/search | Critical |
| Official cultural institutions | Lalit Kala Akademi, Kalakshetra | HTML/search/browser | Critical |
| Chennai institutions | CPB, DakshinaChitra, Goethe-Institut Chennai | HTML/RSS/search | Critical |
| International cultural networks | On the Move, ASEF Culture360, Res Artis | HTML/RSS/search | High |
| Opportunity directories | ArtConnect, TransArtists, ArtDeadline | HTML/search | High |
| Residency networks | Artist Communities Alliance, Res Artis | HTML/search | High |
| Arts organizations | museums, biennales, foundations, galleries | HTML/search | High |
| Cultural institutes | Goethe-Institut, British Council, Institut Français | HTML/search/RSS | High |
| Universities | art schools, research centres, galleries | HTML/search | Medium/High |
| Search engines | Google/Bing-compatible web search | Search API | Discovery |
| Public feeds | RSS/Atom/XML | Feed parser | High |
| Public social announcements | institution-owned pages where permitted | API/search | Secondary |

---

# 9C. Collection Method Priority

AOIA uses the following priority order:

```text
1. Official API
2. Public structured JSON / GraphQL endpoint
3. RSS / Atom / XML feed
4. Static HTML
5. Embedded JSON-LD / schema.org
6. Sitemap / index pages
7. Browser-rendered JavaScript page
8. Search engine discovery
9. Secondary directory
10. Social/web announcement discovery
```

The system should always attempt the cheapest and most stable method before using a browser.

### Important rule

**Search discovers. Official pages verify.**

An opportunity found through ArtConnect, TransArtists, search results, social media, or another directory should be followed to the original provider whenever possible.

---

# 9D. API Collection Layer

APIs are the preferred collection mechanism when a source provides an accessible public API or structured endpoint.

## API sources to support

- REST APIs
- GraphQL APIs
- JSON endpoints
- public search endpoints
- public feeds exposed as JSON
- official application/opportunity APIs
- public event APIs

## API adapter interface

```python
class SourceAPIAdapter:
    source_id: str

    def discover(self):
        ...

    def fetch(self, cursor=None):
        ...

    def normalize(self, item):
        ...

    def get_next_cursor(self, response):
        ...
```

## API safeguards

- respect authentication requirements
- never store private credentials in source records
- respect rate limits
- implement exponential backoff
- cache responses where appropriate
- store API response metadata
- detect pagination
- detect API schema changes
- preserve raw response hashes
- do not repeatedly fetch unchanged pages unnecessarily

---

# 9E. Web Scraping Layer

Web scraping is the main collection mechanism for public opportunity websites without APIs.

## Mode A — HTTP extraction

Use `httpx`/`requests` when the page is server-rendered.

Pipeline:

```text
GET page
 -> HTTP status validation
 -> content-type validation
 -> HTML parser
 -> remove navigation/boilerplate
 -> extract links
 -> extract structured data
 -> extract opportunity text
 -> normalize
```

Recommended Python tools:

- `httpx`
- `BeautifulSoup`
- `selectolax`
- `lxml`
- `trafilatura`

## Mode B — Browser extraction

Use Playwright only when the useful content is rendered dynamically.

```text
URL
 -> Playwright
 -> wait for stable DOM
 -> capture rendered HTML
 -> extract links/data
 -> close browser
```

Browser scraping should be used selectively because it consumes substantially more resources than HTTP collection.

---

# 9F. Structured Web Data Extraction

AOIA should inspect web pages for structured information before attempting expensive language-model extraction.

Priority:

1. JSON-LD
2. schema.org
3. OpenGraph metadata
4. embedded JSON
5. HTML tables
6. semantic headings
7. visible page text

Example targets:

```json
{
  "@type": "Event",
  "name": "Artist Residency",
  "startDate": "2027-01-10",
  "endDate": "2027-03-10",
  "url": "https://example.org/residency"
}
```

For opportunity pages, AOIA should additionally detect fields such as:

```text
deadline
application_deadline
open_date
eligibility
location
country
fee
award
stipend
residency
fellowship
open_call
apply
```

---

# 9G. Sitemap Collection

Sitemaps are a high-value low-cost discovery mechanism.

AOIA should check:

- `/sitemap.xml`
- sitemap indexes
- robots.txt sitemap declarations
- category sitemaps
- opportunity-specific sitemaps

The crawler can use sitemap metadata to identify:

- new pages
- recently modified pages
- opportunity archives
- category pages
- historical opportunity pages

Sitemaps should feed the URL frontier rather than bypass canonical verification.

---

# 9H. RSS / Atom / XML Collection

Feeds are preferred for sources that publish frequent opportunities.

The collector should detect:

- RSS
- Atom
- XML feeds
- category feeds
- opportunity feeds
- news feeds

Store:

- feed URL
- item URL
- publication date
- update date
- title
- summary
- source
- discovered timestamp

Feed items are discovery records. The canonical opportunity page remains the preferred verification source.

---

# 9I. Search Engine Discovery

Search is a first-class discovery sensor.

It is especially important for discovering opportunities that do not appear in directories.

## Search query families

### Chennai

```text
Chennai artist open call
Chennai artist residency
Chennai art fellowship
Chennai artist grant
Chennai photography open call
Chennai visual arts opportunity
Chennai exhibition call artists
Chennai museum internship art
Chennai cultural fellowship
```

### India

```text
India artist open call
India artist residency
India art fellowship
India visual arts grant
India photography residency
India emerging artist award
India public art commission
India museum fellowship
India curator fellowship
```

### International

```text
international artist residency open call
international visual artist fellowship
international photography open call
fully funded artist residency
artist grant no application fee
artist mobility grant
art research fellowship
artist commission open call
new media art residency
AI art residency open call
```

### Deadline-oriented discovery

```text
"open call" artist "deadline" 2026
"applications open" artist residency 2026
"deadline" "artist residency" October 2026
"applications close" "visual artists" 2026
```

### Provider-oriented discovery

```text
site:.gov.in artist fellowship
site:.edu artist residency open call
site:.org artist residency India
site:goethe.de artist open call India
site:britishcouncil.in artist opportunity
site:*.museum artist open call
```

The query generator should dynamically vary:

- geography
- discipline
- opportunity type
- deadline window
- eligibility
- funding condition
- language
- career stage
- technology/art intersection

---

# 9J. Search Result Verification

Search engines must never become the final source of truth.

```text
Search result
     |
     v
Candidate URL
     |
     v
Fetch canonical page
     |
     +--> opportunity confirmed
     |
     +--> page outdated
     |
     +--> page removed
     |
     +--> redirect
     |
     +--> unclear -> verification queue
```

Store both:

- `discovered_via = SEARCH`
- `canonical_source = OFFICIAL_PROVIDER`

when the official provider can be identified.

---

# 9K. Active Source Registry — Chennai

The first deployment should seed a high-priority Chennai source list.

| Source | Primary URL | Why collect it | Method |
|---|---|---|---|
| Chennai Photo Biennale | https://chennaiphotobiennale.foundation/ | Grants, residencies, fellowships, collaborations | HTML/search |
| CPB Open Call | https://opencall.chennaiphotobiennale.com/ | Direct photography calls | HTML |
| Lalit Kala Akademi | https://lalitkala.gov.in/ | Scholarships, studios, events, artist programmes | HTML/search |
| Kalakshetra Foundation | https://kalakshetra.in/ | Arts admissions, internships, programmes, advertisements | HTML/search |
| DakshinaChitra | https://www.dakshinachitra.net/ | Artist exhibitions, internships, cultural programmes | HTML/search |
| Government Museum Chennai | https://govtmuseumchennai.org/ | Announcements, exhibitions and cultural activities | HTML/search |
| Goethe-Institut Chennai | https://www.goethe.de/ins/in/en/sta/che.html | Cultural projects, residencies, calls and collaborations | HTML/search |
| India Art Fair Noticeboard | https://indiaartfair.in/noticeboard | Indian art-world opportunities and announcements | HTML/search |

These sources should be crawled frequently because they are highly relevant to the Chennai output bucket. Current web evidence confirms active opportunity/announcement pages across CPB, Lalit Kala Akademi, Kalakshetra, DakshinaChitra, Goethe-Institut Chennai and India Art Fair. 

---

# 9L. Active Source Registry — India

| Source | URL | Main intelligence |
|---|---|---|
| Ministry of Culture, Government of India | https://culture.gov.in/ | Fellowships, schemes, grants and cultural programmes |
| Indian Council for Cultural Relations | https://iccr.gov.in/ | Artist empanelment, cultural exchange, scholarships, jobs and programmes |
| Lalit Kala Akademi | https://lalitkala.gov.in/ | Visual arts scholarships, studios, events and programmes |
| Sangeet Natak Akademi | https://sangeetnatak.gov.in/ | Performing arts awards, programmes and notices |
| Sahitya Akademi | https://sahitya-akademi.gov.in/ | Literature programmes, awards and fellowships |
| National School of Drama | https://nsd.gov.in/ | Theatre education, programmes and opportunities |
| National Gallery of Modern Art | https://ngmaindia.gov.in/ | Exhibitions, programmes and art activities |
| India Art Fair | https://indiaartfair.in/ | Indian contemporary art ecosystem and noticeboard |
| KHOJ | https://khojstudios.org/ | Residencies, fellowships and contemporary art programmes |
| Serendipity Arts Foundation | https://serendipityarts.org/ | Arts programmes, grants, fellowships and calls |
| Inlaks Shivdasani Foundation | https://www.inlaksfoundation.org/ | Scholarships, grants and arts support |
| Charles Wallace India Trust | https://www.charleswallaceindiatrust.com/ | Arts, heritage and academic fellowships |
| British Council India | https://www.britishcouncil.in/ | Arts, culture, creative economy and exchange opportunities |
| Goethe-Institut India | https://www.goethe.de/ins/in/en/ | Cultural exchange, residencies and project calls |

Official Indian sources should receive higher trust than aggregator listings.

---

# 9M. Active Source Registry — International Opportunity Platforms

The following sites are high-value discovery layers and should form the initial international crawler registry.

| Source | URL | Coverage | Method |
|---|---|---|---|
| ArtConnect | https://www.artconnect.com/ | Open calls, residencies, grants, awards, commissions, jobs | HTML/search |
| TransArtists | https://www.transartists.org/ | International artist residencies and open calls | HTML/search |
| On the Move | https://on-the-move.org/ | Cultural mobility, funding and international opportunities | HTML/RSS/search |
| ASEF Culture360 | https://culture360.asef.org/ | Asia-Europe arts, culture, residencies, grants and open calls | HTML/search |
| Artist Communities Alliance | https://artistcommunities.org/ | Artist residency open calls and deadlines | HTML/search |
| Res Artis | https://resartis.org/ | Global residency network and calls | HTML/search |
| Residency Unlimited | https://residencyunlimited.org/ | Residency and opportunity listings | HTML/search |
| ArtDeadline.Com | https://artdeadline.com/ | Art calls, competitions, fellowships, grants, jobs and residencies | HTML/search |
| Art Jobs | https://www.artjobs.org/ | Art jobs and creative opportunities | HTML/search |
| ArtRabbit | https://www.artrabbit.com/ | Exhibitions, events and art ecosystem discovery | HTML/search |
| e-flux | https://www.e-flux.com/ | Art-world announcements, opportunities and institutional news | HTML/search |
| Rhizome | https://rhizome.org/ | Digital art, technology and media-art opportunities | HTML/search |
| Culture Moves Europe | https://culture.ec.europa.eu/ | European cultural mobility and funding | HTML/search |
| Artists at Risk | https://artistsatrisk.org/ | Support, residencies and emergency resources | HTML/search |
| ArtConnect Magazine | https://www.magazine.artconnect.com/ | Opportunity intelligence and research calls | HTML/search |

TransArtists explicitly focuses on international residencies open to artists from more than one nationality and continuously updates its database, making it a particularly useful discovery layer. Artist Communities Alliance exposes deadline-based and rolling open-call listings. On the Move and ASEF Culture360 are especially valuable for international mobility and Asia-Europe opportunities.

---

# 9N. Source Discovery Expansion

AOIA should not remain dependent on a manually written list of websites.

The Source Discovery Agent should continuously discover additional domains.

```text
Known trusted source
        |
        +--> related organizations
        +--> partner organizations
        +--> funding bodies
        +--> cultural ministries
        +--> museums
        +--> biennales
        +--> residency networks
        +--> universities
        +--> foundations
        +--> artist-run spaces
        v
Candidate source registry
```

## Discovery signals

- external links from trusted providers
- partner lists
- opportunity organizer names
- recurring opportunity providers
- search-result co-occurrence
- RSS/feed links
- sitemap links
- organization directories
- cultural-network membership pages
- institutional partner pages

A discovered source remains `CANDIDATE` until it passes source-quality validation.

---

# 9O. Source Trust Model

Each source receives a dynamic trust score.

```text
Trust(source) =
    Authority
  + Recency
  + UpdateFrequency
  + HistoricalAccuracy
  + OfficialStatus
  + CanonicalEvidence
  - FailureRate
  - Staleness
```

Suggested source classes:

```text
T0 = Official provider / government / institution
T1 = Major cultural network / established opportunity directory
T2 = Established specialist publication or community
T3 = Secondary aggregator
T4 = Unverified discovery source
```

The final opportunity record should retain the source tier.

---

# 9P. Web Collection Scheduling

Collection frequency should depend on opportunity value and source activity.

| Source class | Suggested interval |
|---|---:|
| Critical official source | 1–6 hours |
| Active opportunity directory | 3–12 hours |
| High-value institution | 6–24 hours |
| Normal institution | 24–48 hours |
| Low-volume source | 2–7 days |
| Historical/archive source | weekly/monthly |

The scheduler should become adaptive based on observed change frequency.

```text
If source changes frequently -> crawl more often
If source is stable -> crawl less often
If opportunity is closing soon -> recheck canonical page
If deadline changed recently -> increase verification frequency
```

---

# 9Q. Incremental Web Crawling

AOIA should avoid downloading the same information repeatedly.

Store:

- URL hash
- content hash
- HTTP ETag
- HTTP Last-Modified
- last crawl time
- last successful crawl time
- page version
- link discovery time
- extraction version

Flow:

```text
URL
 |
 +--> HEAD/conditional GET where supported
 |
 +--> unchanged -> skip expensive extraction
 |
 +--> changed -> parse
 |
 +--> compare previous record
 |
 +--> create opportunity version
```

---

# 9R. URL Frontier

AOIA should maintain a persistent URL frontier.

```text
URL Frontier
 |
 +-- priority
 +-- source_id
 +-- URL
 +-- URL type
 +-- last fetched
 +-- next fetch
 +-- failure count
 +-- content hash
 +-- canonical URL
 +-- discovered via
 +-- crawl depth
```

Priority should increase when a URL is:

- an official opportunity page
- an active open-call category
- a deadline listing
- a newly discovered source
- linked from a trusted source
- associated with a high-value opportunity
- likely to contain a changing deadline

---

# 9S. Opportunity Change Detection

AOIA must detect changes, not merely new pages.

Important change types:

```text
NEW_OPPORTUNITY
DEADLINE_CHANGED
APPLICATION_OPENED
APPLICATION_CLOSED
DEADLINE_EXTENDED
ELIGIBILITY_CHANGED
FEE_CHANGED
AWARD_CHANGED
LOCATION_CHANGED
APPLICATION_URL_CHANGED
PROGRAMME_CANCELLED
PAGE_REMOVED
PAGE_REDIRECTED
```

Example:

```text
Previous:
Deadline = 30 Nov 2026

Current:
Deadline = 15 Dec 2026

Event:
DEADLINE_EXTENDED
```

This is one of the highest-value features of AOIA because users should be told when an opportunity they already know about changes.

---

# 9T. Internet Data Quality Gates

Before an opportunity reaches the final user-facing list:

```text
Source discovered
      |
      v
Page reachable?
      |
      v
Opportunity language detected?
      |
      v
Provider identified?
      |
      v
Canonical URL identified?
      |
      v
Deadline parsed or explicitly rolling?
      |
      v
Eligibility evidence found?
      |
      v
Duplicate check
      |
      v
Freshness check
      |
      v
Verification score
      |
      v
Publish
```

Missing information must be represented as `UNKNOWN`, not guessed.

---

# 9U. Web Evidence Model

Every important field should have evidence.

```json
{
  "field": "deadline",
  "value": "2026-10-31",
  "source_url": "https://example.org/open-call",
  "evidence": "Last day for submission: 31 October 2026",
  "extracted_at": "2026-10-04T08:00:00+05:30",
  "confidence": 0.99
}
```

This allows AOIA to answer:

> Why did you say this opportunity is still open?

with the exact page and evidence used.

---

# 9V. Search + Scraping + API Fusion

The strongest architecture is not a single crawler.

```text
                 +------------------+
                 | Official APIs    |
                 +--------+---------+
                          |
                 +--------v---------+
                 | Web Crawlers     |
                 +--------+---------+
                          |
                 +--------v---------+
                 | RSS / Feeds      |
                 +--------+---------+
                          |
                 +--------v---------+
                 | Search Discovery |
                 +--------+---------+
                          |
                 +--------v---------+
                 | Directories      |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Source Resolver  |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Canonicalizer    |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Opportunity NLP  |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Verification     |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Opportunity DB   |
                 +------------------+
```

This architecture prevents AOIA from becoming dependent on one aggregator.

---

# 9W. Recommended Data Collection Stack

## Core backend

- Python 3.12+
- FastAPI
- PostgreSQL
- pgvector
- Redis
- Celery or Arq

## HTTP collection

- httpx
- selectolax
- BeautifulSoup
- lxml
- trafilatura

## Browser collection

- Playwright

## Search

- configurable web-search API
- search result caching
- query templates
- domain-restricted searches

## Structured extraction

- JSON-LD parser
- schema.org parser
- OpenGraph parser
- HTML table parser
- deterministic regex/date extraction

## Lightweight intelligence

- RapidFuzz for duplicate candidates
- small embedding model for semantic similarity
- small classifier for opportunity detection
- Qwen3-0.6B-class model only for ambiguous extraction/normalization

The LLM should be a fallback, not the crawler itself.

---

# 9X. Collection Cost Optimization

The collector should minimize browser and model usage.

```text
Cheap deterministic check
        |
        +--> structured data exists? -> parse
        |
        +--> static HTML? -> parse
        |
        +--> feed exists? -> parse
        |
        +--> sitemap? -> inspect
        |
        +--> dynamic page? -> Playwright
        |
        +--> ambiguity? -> small model
        |
        +--> unresolved? -> verification queue
```

This keeps the system suitable for a small local GPU or CPU deployment.

---

# 9Y. Compliance and Responsible Web Collection

AOIA must respect:

- robots.txt where applicable
- website terms
- API terms
- rate limits
- authentication boundaries
- copyright restrictions
- personal-data minimization
- reasonable request rates
- source attribution

Do not bypass:

- authentication
- paywalls
- CAPTCHAs
- access controls
- private APIs
- technical restrictions

The purpose is opportunity intelligence from publicly accessible web information, not unauthorized extraction.

---

# 9Z. Runtime Collection Output

Every run should produce a collection snapshot.

```text
AOIA RUN
 |
 +-- Chennai opportunities
 +-- India opportunities
 +-- International opportunities
 +-- Newly discovered
 +-- Newly opened
 +-- Currently open
 +-- Closing today
 +-- Closing within 3 days
 +-- Closing within 7 days
 +-- Closing within 14 days
 +-- Closing within 30 days
 +-- Deadline extended
 +-- Deadline changed
 +-- Recently closed
 +-- Upcoming / expected
 +-- Rolling applications
 +-- No-fee opportunities
 +-- Fully funded opportunities
 +-- High-match opportunities
 +-- Verification required
 +-- Sources changed since previous run
```

---

# 9AA. Initial High-Value Source Set

The initial registry should prioritize sources that are demonstrably active on the public web and cover different parts of the opportunity ecosystem.

### Chennai/local

1. Chennai Photo Biennale Foundation
2. CPB Open Call
3. Lalit Kala Akademi Regional Centre Chennai
4. DakshinaChitra
5. Kalakshetra Foundation
6. Government Museum Chennai
7. Goethe-Institut Chennai
8. India Art Fair Noticeboard

### India

9. Ministry of Culture
10. ICCR
11. Lalit Kala Akademi
12. KHOJ
13. Serendipity Arts Foundation
14. Inlaks Foundation
15. Charles Wallace India Trust
16. British Council India
17. Goethe-Institut India
18. National Gallery of Modern Art
19. National School of Drama
20. Sangeet Natak Akademi
21. Sahitya Akademi

### International

22. ArtConnect
23. TransArtists
24. On the Move
25. ASEF Culture360
26. Artist Communities Alliance
27. Res Artis
28. Residency Unlimited
29. ArtDeadline.Com
30. Art Jobs
31. ArtRabbit
32. e-flux
33. Rhizome
34. Culture Moves Europe
35. Artists at Risk

This seed list is not a hard-coded opportunity database. It is a **crawler source registry**. AOIA should continuously discover and validate additional providers.

---

# 9AB. Source Registry Configuration

The registry should be machine-readable.

```yaml
source_id: artconnect
name: ArtConnect
region: international
source_type: opportunity_directory
authority_tier: T1
base_url: https://www.artconnect.com/
collection:
  api: false
  rss: false
  html: true
  browser: false
  search: true
  sitemap: true
priority: 85
crawl_interval_minutes: 360
canonical_verification: required
```

Official provider example:

```yaml
source_id: cpb_foundation
name: Chennai Photo Biennale Foundation
region: chennai
source_type: official_provider
authority_tier: T0
base_url: https://chennaiphotobiennale.foundation/
collection:
  api: false
  rss: false
  html: true
  browser: true
  search: true
priority: 100
crawl_interval_minutes: 180
canonical_verification: source_is_canonical
```

---

# 9AC. Final Data Collection Architecture

The final data-collection philosophy is:

```text
                 INTERNET
                    |
        +-----------+-----------+
        |           |           |
       API        SEARCH      WEB
        |           |           |
        |       discovery      |
        |           |           |
        +-----------+-----------+
                    |
             SOURCE RESOLVER
                    |
             URL FRONTIER
                    |
          HTML / JSON / FEEDS
                    |
             NORMALIZATION
                    |
            CHANGE DETECTION
                    |
             DEDUPLICATION
                    |
             VERIFICATION
                    |
           OPPORTUNITY STORE
                    |
        +-----------+-----------+
        |           |           |
      STATUS      MATCH       RANK
        |           |           |
        +-----------+-----------+
                    |
             AOIA FINAL LIST
```

**Core rule:** AOIA should collect live information from the public internet through APIs, search, feeds and web extraction. It should not require OCR, CSV, Excel, or manually curated offline datasets to operate.

# 11. Source Discovery Agent

AOIA should discover new sources automatically.

``` text
SEARCH
   |
   v
Candidate URL
   |
   v
Source Classifier
   |
   +--> Not relevant → discard
   |
   +--> Relevant
          |
          v
     Trust Evaluation
          |
          v
     Source Registry
          |
          v
     Future Crawling
```

Search concepts can include:

``` text
artist residency
artist fellowship
visual arts grant
artist scholarship
open call contemporary art
artist commission
artist award
biennale open call
museum fellowship
art research grant
international artist residency
emerging artist opportunity
```

------------------------------------------------------------------------

# 12. Opportunity Detection

Before using an LLM, use inexpensive rules.

Signals:

``` text
open call
apply
application
deadline
residency
fellowship
grant
scholarship
competition
award
artist
submission
commission
exhibition
```

If a page has insufficient signals:

``` text
IGNORE
```

If enough signals exist:

``` text
CANDIDATE OPPORTUNITY
```

------------------------------------------------------------------------

# 13. Document Processing

The system should support:

``` text
HTML
PDF
RSS
JSON
XML
Plain Text
Scanned PDF
```

Pipeline:

``` text
Document
   |
   +--> HTML Parser
   |
   +--> PDF Parser
   |
   +--> OCR
   |
   +--> Feed Parser
   |
   v
Normalized Text
```

For PDFs:

``` text
PDF
 |
 v
PyMuPDF
 |
 +--> Text
 +--> Tables
 +--> Metadata
 |
 v
If scanned
 |
 v
OCR
 |
 v
Structured Text
```

------------------------------------------------------------------------

# 14. Lightweight AI Architecture

The system should not send every page to a large language model.

``` text
                    RAW PAGE
                       |
                       v
               RULE-BASED FILTER
                       |
                       v
              SMALL CLASSIFIER
                 /          \
               NO            YES
               |              |
            DISCARD           v
                       RULE EXTRACTION
                              |
                              v
                        STRUCTURED DATA
                              |
                              v
                         VALIDATION
                              |
                     confidence low?
                        /        \
                      NO          YES
                      |            |
                      |            v
                      |       Qwen3-0.6B
                      |            |
                      +------------+
                              |
                              v
                         FINAL RECORD
```

------------------------------------------------------------------------

# 15. Recommended Small Models

## Opportunity Classification

Use a very small model such as:

``` text
SmolLM2-360M
```

Primary uses:

-   opportunity detection
-   type classification
-   simple category classification

## Structured Ambiguity Resolution

Use:

``` text
Qwen3-0.6B
```

Only when deterministic extraction is uncertain.

Uses:

-   ambiguous eligibility
-   complex descriptions
-   funding interpretation
-   requirement interpretation
-   explanation generation

## Semantic Embedding

Use:

``` text
BAAI/bge-small-en-v1.5
```

Uses:

-   artist representation
-   opportunity representation
-   semantic retrieval
-   duplicate detection
-   artist-opportunity matching

------------------------------------------------------------------------

# 16. Deterministic Extraction Layer

Do not use AI for facts that can be extracted reliably.

Use Python libraries for:

``` text
Date
Time
Timezone
Age
Fee
Currency
Email
URL
Country
City
Application deadline
Announcement date
```

Recommended:

``` text
dateparser
regex
Pydantic
RapidFuzz
BeautifulSoup
PyMuPDF
```

Example:

``` text
"Applications close at 23:59 CET on 15 November 2026"

↓

deadline_date = 2026-11-15
deadline_time = 23:59
deadline_timezone = CET
```

------------------------------------------------------------------------

# 17. Opportunity Schema

Every opportunity should become a normalized object.

``` json
{
  "id": "opp_000001",
  "title": "Example Artist Residency",
  "organization": "Example Arts Foundation",
  "type": "residency",

  "location": {
    "city": "Singapore",
    "country": "SG",
    "region": "Asia"
  },

  "eligibility": {
    "age_min": 18,
    "age_max": null,
    "nationalities": [],
    "countries": [],
    "career_stages": [
      "emerging"
    ],
    "mediums": [
      "visual_art"
    ]
  },

  "dates": {
    "announcement_date": "2026-07-12",
    "opening_date": "2026-07-12",
    "deadline_date": "2026-09-30",
    "deadline_time": null,
    "deadline_timezone": null
  },

  "financial": {
    "application_fee": 0,
    "currency": null,
    "stipend": null,
    "travel_support": null,
    "accommodation": null,
    "studio": null
  },

  "requirements": [
    "portfolio",
    "cv",
    "artist_statement"
  ],

  "source": {
    "url": "https://example.org",
    "source_type": "official",
    "trust_score": 1.0
  },

  "status": "open",

  "verification": {
    "confidence": 0.96,
    "last_verified": "2026-10-04T09:00:00+05:30"
  }
}
```

------------------------------------------------------------------------

# 18. Real-Time Status Engine

The status should be calculated every run.

``` python
if now < opening_date:
    status = "UPCOMING"

elif opening_date <= now <= deadline:
    status = "OPEN"

elif deadline < now <= deadline + recently_closed_window:
    status = "RECENTLY_CLOSED"

else:
    status = "EXPIRED"
```

Additional states:

``` text
SUSPENDED
REMOVED
DEADLINE_UNKNOWN
VERIFICATION_REQUIRED
```

------------------------------------------------------------------------

# 19. Deadline Intelligence

Calculate:

``` text
time_remaining = deadline - current_time
```

Then:

``` text
> 90 days       WATCH
61–90 days      PLAN
31–60 days      PREPARE
15–30 days      APPLY SOON
8–14 days       VERY SOON
4–7 days        URGENT
1–3 days        CRITICAL
< 24 hours      FINAL HOURS
```

All calculations must use the opportunity's actual timezone.

------------------------------------------------------------------------

# 20. Geographic Classification

Each opportunity receives:

``` text
geo_scope
```

Possible values:

``` text
CHENNAI
TAMIL_NADU
INDIA
ASIA
INTERNATIONAL
GLOBAL
ONLINE
```

Example:

``` text
Chennai exhibition
→ CHENNAI

Delhi grant accepting Indian artists
→ INDIA

Singapore residency accepting international artists
→ INTERNATIONAL

Online global competition
→ GLOBAL
```

------------------------------------------------------------------------

# 21. Geographic Eligibility vs Location

These must remain separate.

``` text
LOCATION
Where the opportunity occurs.

ELIGIBILITY
Who can apply.
```

Example:

``` text
Location:
London

Eligibility:
Indian artists

Artist:
Chennai

Result:
International opportunity
Eligible
```

------------------------------------------------------------------------

# 22. Artist Profile

The artist profile should contain:

``` text
identity
location
career_stage
education
disciplines
mediums
themes
materials
techniques
practice_description
exhibition_history
residency_history
awards
portfolio
languages
travel_preferences
funding_preferences
opportunity_preferences
career_goals
```

------------------------------------------------------------------------

# 23. Artist Representation

Create:

``` text
artist_text_profile
artist_embedding
artist_constraints
artist_preferences
```

Example:

``` text
Artist:

Location:
Chennai, India

Career:
Emerging

Practice:
Installation + Sculpture + Mixed Media

Themes:
Technology
Human perception
Identity
Spatial experience

Preferred:
Residencies
Fellowships
Exhibitions
Research programmes

Preferred regions:
India
Asia
Europe
Global
```

------------------------------------------------------------------------

# 24. Eligibility Engine

Hard eligibility is deterministic.

``` text
Age
Nationality
Residence
Career stage
Education
Medium
Professional experience
Institutional affiliation
```

Output:

``` text
ELIGIBLE
POSSIBLY_ELIGIBLE
NOT_ELIGIBLE
UNKNOWN
```

Never infer missing facts as positive eligibility.

If the source does not specify:

``` text
UNKNOWN
```

not:

``` text
YES
```

------------------------------------------------------------------------

# 25. Semantic Matching

For eligible opportunities:

``` text
Artist Embedding
       |
       |
       v
Cosine Similarity
       ^
       |
Opportunity Embedding
```

Initial:

``` text
semantic_match = cosine_similarity(
    artist_embedding,
    opportunity_embedding
)
```

------------------------------------------------------------------------

# 26. Final Match Score

Initial scoring:

``` text
MATCH =
    0.25 × Eligibility
  + 0.25 × Practice Match
  + 0.20 × Discipline Match
  + 0.15 × Theme Match
  + 0.10 × Geography
  + 0.05 × Funding Preference
```

All weights should be configurable.

------------------------------------------------------------------------

# 27. Opportunity Quality Score

Separate artist fit from opportunity quality.

``` text
QUALITY =
    Institutional Reputation
  + Funding Quality
  + Career Value
  + Transparency
  + Artist Support
  + International Reach
  - Application Cost
  - Risk
```

Normalize:

``` text
0–100
```

------------------------------------------------------------------------

# 28. Priority Score

Final actionable priority:

``` text
PRIORITY =
    MATCH
  × ELIGIBILITY_CONFIDENCE
  × QUALITY
  × URGENCY
  × USER_PREFERENCE
```

This prevents an irrelevant opportunity with an approaching deadline
from dominating the dashboard.

------------------------------------------------------------------------

# 29. Application Effort

Every opportunity should estimate application effort.

``` text
LOW
MEDIUM
HIGH
VERY_HIGH
```

Signals:

``` text
portfolio
CV
statement
proposal
budget
references
video
translation
recommendation letters
application fee
```

This enables:

``` text
High Match + Low Effort = EASY WIN
High Match + High Effort = STRATEGIC
Low Match + High Effort = LOW PRIORITY
```

------------------------------------------------------------------------

# 30. Primary Output Lists

Every run must generate:

``` text
1. NEW OPPORTUNITIES

2. CURRENTLY OPEN

3. CLOSING TODAY

4. CLOSING IN 3 DAYS

5. CLOSING IN 7 DAYS

6. CLOSING IN 14 DAYS

7. CLOSING IN 30 DAYS

8. CHENNAI

9. INDIA

10. INTERNATIONAL

11. ONLINE / GLOBAL

12. NO APPLICATION FEE

13. FULLY FUNDED / HIGH FUNDING

14. HIGH MATCH

15. EASY WINS

16. RECENTLY CLOSED

17. UPCOMING / EXPECTED

18. UPDATED SINCE LAST RUN

19. DEADLINE CHANGED

20. VERIFICATION REQUIRED
```

------------------------------------------------------------------------

# 31. Recommended Dashboard

``` text
============================================================
AOIA
ART OPPORTUNITY INTELLIGENCE
============================================================

LAST RUN
04 OCT 2026 — 09:30 IST

SOURCES
127 checked
31 changed
96 unchanged

------------------------------------------------------------
CHENNAI
------------------------------------------------------------

New                  8
Open                21
Closing Soon         6
No Fee               4

------------------------------------------------------------
INDIA
------------------------------------------------------------

New                 19
Open                74
Closing Soon        18
High Match          11

------------------------------------------------------------
INTERNATIONAL
------------------------------------------------------------

New                 15
Open               183
Closing Soon        42
High Match          27

------------------------------------------------------------
ACTION NOW
------------------------------------------------------------

CRITICAL             3
URGENT               8
VERY SOON           14

------------------------------------------------------------
NO APPLICATION FEE
------------------------------------------------------------

23 opportunities

------------------------------------------------------------
TOP MATCHES
------------------------------------------------------------

1. Opportunity A     96%     3 days
2. Opportunity B     94%     7 days
3. Opportunity C     92%    14 days
4. Opportunity D     90%    22 days

------------------------------------------------------------
RECENTLY CLOSED
------------------------------------------------------------

12 opportunities

------------------------------------------------------------
UPCOMING
------------------------------------------------------------

9 predicted recurring opportunities

============================================================
```

------------------------------------------------------------------------

# 32. Run Modes

The system should support multiple modes.

## Manual

``` bash
python -m aoia run
```

Produces a fresh snapshot.

## Regional

``` bash
python -m aoia run --region chennai
```

## India

``` bash
python -m aoia run --region india
```

## International

``` bash
python -m aoia run --region international
```

## Closing Soon

``` bash
python -m aoia run --closing-soon 30
```

## Full

``` bash
python -m aoia run --all
```

------------------------------------------------------------------------

# 33. Scheduled Mode

Production operation:

``` text
Every hour
    ↓
check high-priority / changing sources

Every 6 hours
    ↓
check active opportunity sources

Daily
    ↓
full discovery

Weekly
    ↓
source discovery + source health

Monthly
    ↓
recurrence / trend analysis
```

------------------------------------------------------------------------

# 34. Incremental Crawling

Do not reprocess everything.

Store:

``` text
etag
last_modified
content_hash
page_hash
last_checked
last_changed
```

If:

``` text
content_hash == previous_hash
```

then:

``` text
SKIP AI PROCESSING
```

If changed:

``` text
REPROCESS
```

------------------------------------------------------------------------

# 35. Opportunity Versioning

Never silently overwrite opportunity information.

``` text
Opportunity
|
+-- Version 1
|   deadline = Nov 30
|
+-- Version 2
|   deadline = Dec 15
|
+-- Version 3
    fee = changed
```

This enables:

``` text
deadline change detection
eligibility change detection
fee change detection
funding change detection
requirement change detection
```

------------------------------------------------------------------------

# 36. Duplicate Detection

The same opportunity may appear on several websites.

Use:

``` text
Exact URL
Organization
Title
Deadline
Location
Description similarity
Embeddings
```

Pipeline:

``` text
Exact Match
   ↓
Fuzzy Match
   ↓
Semantic Match
   ↓
Canonical Record
```

The official source should become the canonical record whenever
possible.

------------------------------------------------------------------------

# 37. Verification Engine

Every record receives:

``` text
CONFIRMED
LIKELY
UNVERIFIED
EXPIRED
CLOSED
REMOVED
```

A confirmed opportunity should preferably contain:

``` text
official source
explicit deadline
application mechanism
consistent requirements
recent verification
```

------------------------------------------------------------------------

# 38. Confidence Model

Each extracted field may have confidence.

``` json
{
  "deadline": {
    "value": "2026-11-30",
    "confidence": 0.99
  },
  "funding": {
    "value": "not specified",
    "confidence": 0.88
  },
  "eligibility": {
    "value": "international",
    "confidence": 0.96
  }
}
```

If confidence is low:

``` text
REVIEW_REQUIRED
```

------------------------------------------------------------------------

# 39. Human-in-the-Loop

Human review should only be required for difficult cases.

``` text
AI Confidence
      |
      +--> HIGH → automatic
      |
      +--> MEDIUM → secondary validation
      |
      +--> LOW → human review
```

Review categories:

``` text
ambiguous eligibility
ambiguous deadline
conflicting source information
suspicious opportunity
duplicate conflict
funding ambiguity
```

------------------------------------------------------------------------

# 40. Scam / Risk Detection

Detect observable risk indicators:

``` text
unclear organizer
excessive application fee
inconsistent information
unclear selection process
suspicious payment requirements
missing institutional identity
copied opportunity content
unusual contractual requirements
```

Output:

``` text
LOW_RISK
MEDIUM_RISK
REVIEW_REQUIRED
```

The system should describe observable signals and avoid unsupported
accusations.

------------------------------------------------------------------------

# 41. Database Architecture

Use:

``` text
PostgreSQL
+
pgvector
```

Core tables:

``` text
artists
artist_practices
artist_artworks
artist_preferences

organizations

sources
source_checks
source_events

opportunities
opportunity_eligibility
opportunity_requirements
opportunity_funding
opportunity_locations
opportunity_versions

opportunity_embeddings
artist_embeddings

matches
match_explanations

applications
application_assets
application_events

notifications
deadline_events

run_snapshots
run_statistics

recurring_opportunities
opportunity_history
```

------------------------------------------------------------------------

# 42. Run Snapshot

Every execution should create:

``` json
{
  "run_id": "run_2026_10_04_0930",
  "timestamp": "2026-10-04T09:30:00+05:30",

  "sources_checked": 127,
  "sources_changed": 31,

  "new_opportunities": 42,
  "updated_opportunities": 18,
  "expired_opportunities": 11,
  "duplicates_removed": 27,

  "chennai": 21,
  "india": 74,
  "international": 183,

  "closing_soon": 42
}
```

This allows historical system evaluation.

------------------------------------------------------------------------

# 43. Opportunity History

Maintain:

``` text
first_seen
last_seen
last_verified
opened_date
deadline_date
closed_date
status_history
source_history
```

This allows the system to learn:

``` text
When does this organization normally open?
How long does the call remain open?
Does the deadline usually get extended?
Does the opportunity recur annually?
```

------------------------------------------------------------------------

# 44. Recurrence Prediction

For recurring opportunities:

``` text
2023 → October
2024 → October
2025 → September
2026 → October
```

The system may produce:

``` text
Expected next opening:
September–October 2027

Confidence:
MEDIUM
```

Important:

``` text
PREDICTED ≠ CONFIRMED
```

------------------------------------------------------------------------

# 45. Opportunity Graph

Future version:

``` text
Artist
   |
   +-- practices --> Sculpture
   |
   +-- explores --> Technology
   |
   +-- located --> Chennai
   |
   +-- eligible_for --> Residency
                         |
                         +--> Organization
                         +--> Country
                         +--> Funding
                         +--> Deadline
```

This supports graph-based discovery and recommendations.

------------------------------------------------------------------------

# 46. Complete Agent Architecture

``` text
                    AOIA ORCHESTRATOR
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
 SOURCE AGENT       COLLECTION AGENT     TIME AGENT
        |                  |                  |
        v                  v                  v
 Source Registry       Raw Documents      Current Time
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                 OPPORTUNITY AGENT
                           |
                           v
                 EXTRACTION AGENT
                           |
                           v
                 VALIDATION AGENT
                           |
                           v
                DEDUPLICATION AGENT
                           |
                           v
                 DATABASE AGENT
                           |
             +-------------+-------------+
             |                           |
             v                           v
       MATCHING AGENT             DEADLINE AGENT
             |                           |
             +-------------+-------------+
                           |
                           v
                   RANKING AGENT
                           |
                           v
                  REPORTING AGENT
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Dashboard      JSON       Notifications
                           |
                           v
                    FEEDBACK AGENT
                           |
                           v
                    LEARNING LOOP
```

------------------------------------------------------------------------

# 47. Agent Responsibilities

## Source Agent

Find and maintain sources.

## Collection Agent

Fetch source content.

## Opportunity Agent

Detect potential opportunities.

## Extraction Agent

Convert content to structured records.

## Validation Agent

Verify facts and confidence.

## Deduplication Agent

Resolve duplicate opportunities.

## Database Agent

Persist and version information.

## Matching Agent

Calculate artist compatibility.

## Deadline Agent

Calculate temporal state.

## Ranking Agent

Prioritize opportunities.

## Reporting Agent

Generate the current snapshot.

## Notification Agent

Send only actionable changes.

## Feedback Agent

Learn from artist actions.

------------------------------------------------------------------------

# 48. Python Project Structure

``` text
aoia/
|
+-- app/
|   |
|   +-- api/
|   +-- auth/
|   +-- config/
|   |
|   +-- agents/
|   |   +-- orchestrator.py
|   |   +-- source_agent.py
|   |   +-- collection_agent.py
|   |   +-- opportunity_agent.py
|   |   +-- extraction_agent.py
|   |   +-- validation_agent.py
|   |   +-- dedup_agent.py
|   |   +-- matching_agent.py
|   |   +-- deadline_agent.py
|   |   +-- ranking_agent.py
|   |   +-- reporting_agent.py
|   |   +-- notification_agent.py
|   |
|   +-- discovery/
|   |   +-- crawlers/
|   |   +-- search/
|   |   +-- feeds/
|   |   +-- source_registry/
|   |
|   +-- extraction/
|   |   +-- html/
|   |   +-- pdf/
|   |   +-- ocr/
|   |   +-- rules/
|   |   +-- llm/
|   |
|   +-- matching/
|   |   +-- eligibility/
|   |   +-- embeddings/
|   |   +-- ranking/
|   |
|   +-- temporal/
|   |   +-- deadlines/
|   |   +-- recurrence/
|   |   +-- snapshots/
|   |
|   +-- notifications/
|   |
|   +-- database/
|   |
|   +-- models/
|   |
|   +-- schemas/
|   |
|   +-- services/
|   |
|   +-- tests/
|
+-- configs/
|   +-- sources/
|   +-- taxonomy.yaml
|   +-- ranking.yaml
|   +-- regions.yaml
|
+-- models/
|   +-- qwen/
|   +-- embeddings/
|
+-- scripts/
|
+-- docker/
|
+-- docs/
|
+-- requirements.txt
+-- docker-compose.yml
+-- README.md
```

------------------------------------------------------------------------

# 49. Technology Stack

``` text
Frontend
React
Vite
Tailwind CSS

Backend
Python
FastAPI

Database
PostgreSQL
pgvector

Crawler
httpx
BeautifulSoup
Playwright

Document Processing
PyMuPDF
OCR

ML
PyTorch
Transformers
Sentence Transformers

Small LLM
Qwen3-0.6B

Tiny Classifier
SmolLM2-360M or lightweight classifier

Embeddings
BGE-small-en-v1.5

Similarity
FAISS or pgvector

Fuzzy Matching
RapidFuzz

Scheduling
Celery
Redis

Deployment
Docker

Monitoring
Prometheus
Grafana

Notifications
Email
Telegram
Discord
Web Push
```

------------------------------------------------------------------------

# 50. API Architecture

## Run

``` http
POST /api/v1/runs
```

## Current snapshot

``` http
GET /api/v1/opportunities/current
```

## Chennai

``` http
GET /api/v1/opportunities?region=chennai
```

## India

``` http
GET /api/v1/opportunities?region=india
```

## International

``` http
GET /api/v1/opportunities?region=international
```

## Closing soon

``` http
GET /api/v1/opportunities/closing-soon?days=30
```

## Recently closed

``` http
GET /api/v1/opportunities/recently-closed?days=30
```

## New

``` http
GET /api/v1/opportunities/new?days=7
```

## Top matches

``` http
GET /api/v1/matches/top
```

## Opportunity

``` http
GET /api/v1/opportunities/{id}
```

------------------------------------------------------------------------

# 51. CLI Architecture

``` bash
# Full refresh
python -m aoia run

# Chennai
python -m aoia run --region chennai

# India
python -m aoia run --region india

# International
python -m aoia run --region international

# Everything
python -m aoia run --all

# Closing within 30 days
python -m aoia closing --days 30

# New opportunities
python -m aoia new --days 7

# Recently closed
python -m aoia closed --days 30

# Source discovery
python -m aoia discover-sources

# Verify sources
python -m aoia verify

# Generate report
python -m aoia report

# Rebuild embeddings
python -m aoia embeddings
```

------------------------------------------------------------------------

# 52. JSON Output

Every run should produce:

``` text
outputs/
|
+-- latest.json
+-- latest.csv
+-- latest.md
|
+-- snapshots/
|   +-- 2026-10-04T0930.json
|   +-- 2026-10-04T1530.json
|
+-- reports/
    +-- chennai.md
    +-- india.md
    +-- international.md
    +-- closing-soon.md
```

------------------------------------------------------------------------

# 53. Markdown Report Format

Every run should generate:

``` markdown
# Art Opportunity Intelligence

Run: 04 October 2026 — 09:30 IST

## Chennai

### Closing Soon

| Opportunity | Type | Deadline | Fee | Match |
|---|---|---:|---:|---:|

### Newly Opened

...

### Currently Open

...

## India

...

## International

...

## Recently Closed

...

## Updated Opportunities

...

## Deadline Changes

...

## High Match

...

## No Application Fee

...

## Verification Required

...
```

------------------------------------------------------------------------

# 54. Notification Logic

Do not notify for everything.

Notify when:

``` text
new high-match opportunity
deadline < 30 days
deadline changed
eligibility changed
funding changed
application portal changed
high-priority opportunity discovered
```

Example:

``` text
AOIA ALERT

New High-Match Opportunity

International Artist Residency

Match: 94%
Deadline: 18 days
Application Fee: None

Why:
- international artists accepted
- installation accepted
- emerging artists eligible
- strong thematic match

Action:
Begin application preparation.
```

------------------------------------------------------------------------

# 55. Source Change Alert

If:

``` text
Old deadline = 30 Nov
New deadline = 15 Dec
```

send:

``` text
DEADLINE CHANGED

Opportunity:
Example Residency

Previous:
30 November

Current:
15 December

Source:
Official organization

Verified:
04 October 2026
```

------------------------------------------------------------------------

# 56. Safety and Reliability

The system must assume that external web content is untrusted.

Never allow webpage text to modify:

``` text
system prompts
database commands
application logic
credentials
agent instructions
```

Use:

``` text
content isolation
HTML sanitization
URL validation
sandboxed browser execution
prompt-injection-resistant extraction
```

------------------------------------------------------------------------

# 57. Evaluation

Create an annotated benchmark.

Target:

``` text
1,000+ opportunities
```

Annotate:

``` text
opportunity type
deadline
eligibility
location
fee
funding
medium
requirements
duplicate identity
artist relevance
```

Metrics:

``` text
Extraction:
Precision
Recall
F1

Deadline:
Exact date accuracy

Duplicate:
Precision
Recall

Matching:
Precision@K
Recall@K
NDCG

Source discovery:
Relevant source precision

Freshness:
Time from source update to database update
```

------------------------------------------------------------------------

# 58. Real-Time Freshness Metric

Introduce:

``` text
Opportunity Freshness =
current_time - last_verified_time
```

Classify:

``` text
< 6h       LIVE
6–24h      FRESH
1–3 days   RECENT
3–7 days   AGING
> 7 days   STALE
```

Critical opportunities should be rechecked more frequently.

------------------------------------------------------------------------

# 59. Adaptive Crawling

Not every source needs the same frequency.

``` text
High-value active source
→ every 1–6 hours

Normal source
→ every 12–24 hours

Low-volume source
→ every 2–7 days

Historical source
→ weekly/monthly
```

The crawler can automatically increase frequency when:

``` text
deadline approaching
source changes frequently
new opportunities detected
source historically reliable
```

------------------------------------------------------------------------

# 60. Final End-to-End Execution

``` text
START
 |
 v
Load artist profile
 |
 v
Load source registry
 |
 v
Get current time
 |
 v
Select sources due for refresh
 |
 v
Fetch source
 |
 v
Detect changes
 |
 +---- NO CHANGE ----> next source
 |
 +---- CHANGE
        |
        v
    Parse content
        |
        v
    Detect opportunity
        |
        v
    Extract facts
        |
        v
    Normalize
        |
        v
    Validate
        |
        v
    Deduplicate
        |
        v
    Store/version
        |
        v
    Generate embedding
        |
        v
    Match artist
        |
        v
    Calculate deadline state
        |
        v
    Calculate priority
        |
        v
    Add to snapshot
        |
        v
NEXT SOURCE
        |
        v
SNAPSHOT COMPLETE
        |
        v
GENERATE REPORTS
        |
        +--> Chennai
        +--> India
        +--> International
        +--> Closing Soon
        +--> New
        +--> Recently Closed
        +--> High Match
        +--> No Fee
        +--> Updated
        |
        v
SEND IMPORTANT ALERTS
        |
        v
SAVE SNAPSHOT
        |
        v
END
```

------------------------------------------------------------------------

# 61. MVP Implementation Order

## Phase 1 --- Real-Time Discovery

Build:

``` text
source registry
crawler
HTML parser
PDF parser
opportunity schema
PostgreSQL
```

Goal:

> Collect real opportunities.

## Phase 2 --- Temporal Intelligence

Build:

``` text
opening date
deadline
status
closing-soon buckets
recently-closed
snapshots
```

Goal:

> Know what is available right now.

## Phase 3 --- Geographic Intelligence

Build:

``` text
Chennai
India
International
Online
```

Goal:

> Organize opportunities by location and eligibility.

## Phase 4 --- AI Extraction

Build:

``` text
small classifier
Qwen3-0.6B fallback
confidence system
```

Goal:

> Understand unstructured opportunity information.

## Phase 5 --- Matching

Build:

``` text
artist profile
BGE-small embeddings
eligibility rules
semantic matching
ranking
```

Goal:

> Find opportunities relevant to the artist.

## Phase 6 --- Notifications

Build:

``` text
Email
Telegram
Dashboard
```

Goal:

> Alert only when action matters.

## Phase 7 --- Learning

Build:

``` text
feedback
application outcomes
ranking learning
recurrence prediction
```

Goal:

> Improve recommendations over time.

------------------------------------------------------------------------

# 62. Recommended First Deployment

For the first operational version:

``` text
ONE ARTIST
        |
        v
30–50 HIGH-QUALITY SOURCES
        |
        v
100–1,000 OPPORTUNITIES
        |
        v
REAL-TIME NORMALIZATION
        |
        v
CHENNAI / INDIA / INTERNATIONAL
        |
        v
DEADLINE INTELLIGENCE
        |
        v
PERSONALIZED RANKING
```

Do not begin with thousands of websites.

The objective of version 1 is **accuracy and freshness**, not maximum
volume.

------------------------------------------------------------------------

# 63. Final Architecture Principle

AOIA should follow this rule:

> **The system should never merely tell the artist what exists. It
> should tell the artist what exists now, what is relevant, what is
> closing, what changed, what is worth applying to, and what action
> should happen next.**

The transformation is:

``` text
OLD MODEL

Search
 ↓
Read
 ↓
Filter
 ↓
Remember deadline
 ↓
Apply


AOIA MODEL

Continuous Discovery
 ↓
Real-Time Verification
 ↓
Opportunity Understanding
 ↓
Geographic Classification
 ↓
Eligibility Analysis
 ↓
Practice Matching
 ↓
Quality Assessment
 ↓
Deadline Intelligence
 ↓
Priority Ranking
 ↓
Action Recommendation
 ↓
Application
 ↓
Outcome
 ↓
Learning
```

------------------------------------------------------------------------

# 64. Final System Definition

**Art Opportunity Intelligence Agent (AOIA)** is a lightweight,
continuously updating, source-aware, temporal recommendation system that
converts fragmented public art-opportunity information into a real-time
personalized opportunity intelligence layer.

Its core computational philosophy is:

``` text
RULES FIRST
      +
SMALL MODELS
      +
SEMANTIC EMBEDDINGS
      +
LLM ONLY FOR AMBIGUITY
      +
SOURCE VERIFICATION
      +
TEMPORAL INTELLIGENCE
      +
HUMAN OVERSIGHT
```

The final objective is:

``` text
                 FIND
                  ↓
               VERIFY
                  ↓
              UNDERSTAND
                  ↓
               MATCH
                  ↓
               RANK
                  ↓
             PRIORITIZE
                  ↓
               ALERT
                  ↓
               APPLY
                  ↓
               LEARN
                  ↓
              FIND BETTER
```

**AOIA is therefore not an art-opportunity directory.**

It is an **autonomous Art Opportunity Intelligence System** designed to
provide a fresh, verified and actionable opportunity landscape every
time it runs.
