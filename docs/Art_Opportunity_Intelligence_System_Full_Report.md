# Art Opportunity Intelligence System
## AI-Powered Discovery, Matching, Deadline Intelligence, and Application Management for Artists

**Version:** 1.0  
**Date:** October 2026  
**Document Type:** Product + Technical System Design  
**Status:** Proposed / Research & Development Concept

---

# 1. Executive Summary

The **Art Opportunity Intelligence System (AOIS)** is an AI-powered platform designed to continuously discover, structure, evaluate, rank, and monitor opportunities available to artists.

The system goes beyond a conventional search engine or open-call directory. Instead of asking an artist to repeatedly search hundreds of websites for residencies, exhibitions, grants, competitions, fellowships, biennales, art fairs, institutional programmes, and other opportunities, AOIS continuously monitors permitted public sources and transforms unstructured opportunity information into a personalized opportunity intelligence layer.

The central idea is:

> **Do not make artists search for opportunities. Make opportunities find the artists who are eligible and relevant.**

The system maintains an evolving artist profile containing information such as:

- artistic disciplines
- mediums
- practice themes
- career stage
- geographic eligibility
- education
- exhibition history
- portfolio information
- professional experience
- funding requirements
- residency preferences
- travel constraints
- application preferences

Every discovered opportunity is converted into structured data and passed through an AI eligibility and relevance engine.

The system then produces:

- opportunity matches
- eligibility analysis
- relevance scores
- deadline countdowns
- preparation reminders
- source verification status
- application requirement summaries
- risk or ambiguity warnings
- personalized recommendations

A major feature is **deadline intelligence**.

For example:

> **International Sculpture Residency**  
> Deadline: 30 November 2026  
> 27 days remaining  
> Match: High  
> International artists: Yes  
> Sculpture / Installation: Yes  
> Application fee: None  
> Portfolio required: Yes  
> Suggested action: Begin portfolio and proposal preparation.

The platform therefore becomes an **opportunity intelligence assistant for artists**, rather than simply another database of links.

---

# 2. Problem Statement

Artists face a fragmented opportunity ecosystem.

Relevant opportunities may be distributed across:

- gallery websites
- museum websites
- university websites
- residency organisations
- government cultural institutions
- foundations
- biennales
- art fairs
- artist networks
- grant portals
- competition websites
- cultural ministries
- social media announcements
- newsletters
- institutional mailing lists
- independent art organisations

The information is often presented in inconsistent formats.

One website may provide:

> Deadline: 15 November

Another may state:

> Applications close at 23:59 CET on November 15.

Another may provide the deadline only inside a PDF.

Another may publish eligibility requirements in a separate page.

Another may announce an opportunity on social media and direct applicants to an external form.

This creates several problems.

## 2.1 Discovery Problem

Artists must manually search across many sources.

## 2.2 Information Fragmentation

Important information is distributed across multiple pages and documents.

## 2.3 Eligibility Uncertainty

An opportunity may look relevant but contain restrictions based on:

- nationality
- residency
- age
- career stage
- medium
- education
- years of practice
- institutional affiliation
- geographic location

## 2.4 Deadline Risk

Artists frequently discover opportunities too late.

An opportunity discovered one day before the deadline may technically be relevant but practically useless because the artist still needs to prepare:

- portfolio
- artist statement
- CV
- project proposal
- references
- translations
- images
- video
- budget
- recommendation letters

## 2.5 Opportunity Overload

A large number of opportunities can create another problem:

> More information does not necessarily produce more applications.

The system therefore needs **intelligent prioritization**, not simply aggregation.

---

# 3. Vision

The long-term vision is to create an intelligent infrastructure layer between artists and the global art-opportunity ecosystem.

The platform should answer four questions:

1. **What opportunities exist?**
2. **Am I eligible?**
3. **Is this opportunity actually relevant to my practice?**
4. **When should I act?**

The ideal experience becomes:

```text
Artist Profile
      |
      v
Continuous Discovery
      |
      v
Opportunity Understanding
      |
      v
Eligibility Analysis
      |
      v
Practice Matching
      |
      v
Priority Ranking
      |
      v
Deadline Intelligence
      |
      v
Application Preparation
      |
      v
Outcome Tracking
      |
      v
Learning System
```

---

# 4. Core Concept

AOIS can be understood as a combination of five systems:

```text
+-------------------------------------------------------+
|              ART OPPORTUNITY INTELLIGENCE             |
+-------------------------------------------------------+
|                                                       |
|  1. Opportunity Discovery Engine                     |
|                                                       |
|  2. Opportunity Understanding Engine                 |
|                                                       |
|  3. Artist-Opportunity Matching Engine               |
|                                                       |
|  4. Deadline & Alert Intelligence                    |
|                                                       |
|  5. Application Intelligence & Learning              |
|                                                       |
+-------------------------------------------------------+
```

The five systems work together to convert raw web information into actionable decisions.

---

# 5. Target Users

## 5.1 Emerging Artists

Artists seeking:

- first residencies
- exhibitions
- grants
- competitions
- international exposure

## 5.2 Professional Artists

Artists seeking:

- international exhibitions
- institutional residencies
- production grants
- fellowships
- biennales
- museum programmes

## 5.3 Art Students

Students seeking:

- student competitions
- graduate residencies
- scholarships
- exhibitions
- portfolio opportunities

## 5.4 Curators

Curators may use the system to discover:

- artists
- open calls
- institutional programmes
- exhibition opportunities

## 5.5 Art Organisations

Organisations could eventually use the platform to:

- publish opportunities
- discover artists
- manage open calls
- identify suitable applicant pools

---

# 6. Opportunity Taxonomy

The system should not treat every opportunity as the same type.

A unified taxonomy can include:

```text
ART OPPORTUNITIES
|
+-- Exhibitions
|   +-- Group Exhibition
|   +-- Solo Exhibition
|   +-- Online Exhibition
|   +-- Institutional Exhibition
|
+-- Residencies
|   +-- Studio Residency
|   +-- Production Residency
|   +-- Research Residency
|   +-- Fellowship Residency
|
+-- Grants
|   +-- Production Grant
|   +-- Travel Grant
|   +-- Research Grant
|   +-- Project Grant
|
+-- Competitions
|   +-- Painting
|   +-- Sculpture
|   +-- Digital Art
|   +-- Installation
|   +-- Multidisciplinary
|
+-- Fellowships
|
+-- Biennales
|
+-- Art Fairs
|
+-- Awards
|
+-- Scholarships
|
+-- Commissions
|
+-- Workshops
|
+-- Institutional Programmes
|
+-- Research Opportunities
```

This taxonomy allows users to filter and prioritize opportunities according to their goals.

---

# 7. System Architecture

The proposed architecture is:

```text
                         INTERNET
                            |
          +-----------------+------------------+
          |                 |                  |
       Websites          RSS/APIs          Public Feeds
          |                 |                  |
          +-----------------+------------------+
                            |
                            v
                +-----------------------+
                | Discovery Layer       |
                | Search / Crawlers     |
                | Source Connectors     |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Extraction Layer      |
                | HTML / PDF / Forms    |
                | OCR where necessary   |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | AI Structuring        |
                | LLM / NLP Extraction  |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Validation Layer      |
                | Dates / Eligibility   |
                | Source Verification   |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Opportunity Database  |
                +-----------+-----------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
    +-------------------+        +-------------------+
    | Artist Profile    |        | Application Data  |
    | Knowledge Model   |        | & History         |
    +---------+---------+        +---------+---------+
              |                            |
              +-------------+--------------+
                            |
                            v
                +-----------------------+
                | Matching Engine       |
                | Eligibility + Fit     |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Ranking Engine        |
                | Priority / Confidence |
                +-----------+-----------+
                            |
                            v
                +-----------------------+
                | Deadline Intelligence |
                +-----------+-----------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
          Web Dashboard             Alerts
                                  Email / App
                                  Telegram /
                                  Other channels
```

---

# 8. Module 1 — Opportunity Discovery Engine

The discovery engine continuously identifies potential opportunities.

## 8.1 Sources

Potential sources include:

- official institutional websites
- gallery websites
- museum websites
- residency websites
- cultural organisations
- universities
- government arts departments
- foundations
- grant organisations
- public RSS feeds
- permitted search results
- publicly accessible announcement pages
- structured APIs
- artist opportunity directories

## 8.2 Source Priority

The system should prioritize sources using a trust hierarchy:

```text
Tier 1
Official opportunity provider
        |
Tier 2
Official partner / institution
        |
Tier 3
Established opportunity directory
        |
Tier 4
Community / social announcement
        |
Tier 5
Unverified third-party source
```

The system should preserve the original source URL for every opportunity.

---

# 9. Responsible Web Collection

The system must not treat the entire web as unrestricted data.

The collection layer should respect:

- robots.txt where applicable
- website terms
- rate limits
- copyright restrictions
- API policies
- authentication requirements
- platform-specific automation rules

The system should preferably use:

1. official APIs
2. RSS feeds
3. public feeds
4. permitted crawling
5. search/indexing services
6. manually configured sources

The system should store structured facts rather than unnecessarily reproducing complete source pages.

Each opportunity should retain:

```text
source_url
source_domain
source_name
source_type
last_checked
last_verified
verification_status
```

---

# 10. Module 2 — Opportunity Extraction Engine

Raw pages are often unstructured.

The extraction engine converts them into a normalized opportunity schema.

For example:

```json
{
  "title": "International Sculpture Residency",
  "organization": "Example Arts Foundation",
  "type": "residency",
  "country": "United Kingdom",
  "city": "London",
  "deadline": "2026-11-30",
  "application_fee": 0,
  "eligibility": {
    "international_artists": true,
    "career_stage": ["emerging", "mid-career"],
    "mediums": ["sculpture", "installation"]
  },
  "funding": {
    "studio": true,
    "accommodation": true,
    "travel": false,
    "stipend": null
  },
  "requirements": [
    "portfolio",
    "artist_statement",
    "cv",
    "project_proposal"
  ],
  "source_url": "...",
  "verification_status": "official"
}
```

---

# 11. Extraction from PDFs

Many art opportunities are published as PDFs.

Therefore the pipeline should support:

```text
PDF
 |
 v
Text Extraction
 |
 +--> Tables
 |
 +--> Dates
 |
 +--> Eligibility
 |
 +--> Application requirements
 |
 +--> Funding
 |
 v
Structured Opportunity
```

For scanned PDFs:

```text
PDF
 |
 v
Page Rendering
 |
 v
OCR
 |
 v
Text Reconstruction
 |
 v
AI Extraction
```

The system should maintain confidence scores for extracted information.

---

# 12. Opportunity Normalization

Different sources may describe the same information differently.

For example:

```text
"Deadline: 15 Nov 2026"

"Applications close November 15"

"Last date: 15/11/2026"

"Submit before 23:59 CET, 15 November"
```

These should become:

```text
deadline_date = 2026-11-15
deadline_time = 23:59
deadline_timezone = CET
```

This normalized structure makes automated reminders possible.

---

# 13. Duplicate Detection

The same opportunity may appear on:

- official website
- ArtConnect
- Instagram
- university page
- opportunity directory
- newsletter

The system needs entity resolution.

Possible duplicate signature:

```text
organization
+
title similarity
+
deadline
+
location
```

A combination of:

- exact matching
- fuzzy string matching
- semantic embeddings

can identify duplicates.

The canonical record should point to the most authoritative source.

---

# 14. Opportunity Verification

Every opportunity should have a verification state.

```text
CONFIRMED
LIKELY
UNVERIFIED
EXPIRED
CLOSED
REMOVED
```

A confirmed opportunity should preferably have:

- accessible official source
- explicit deadline
- clear application mechanism
- consistent information

If the AI cannot confidently determine a fact, it should say so.

For example:

> Travel funding: Not specified.

rather than:

> Travel funding: No.

This distinction prevents hallucinated information.

---

# 15. Artist Profile Engine

The artist profile is the foundation of personalized matching.

The profile should combine structured and unstructured information.

## 15.1 Structured Profile

```text
Artist Name
Country
City
Nationality
Career Stage
Education
Disciplines
Mediums
Years of Practice
Exhibition History
Residency History
Awards
Publications
Languages
Travel Constraints
Funding Preferences
Residency Preferences
```

## 15.2 Practice Profile

The system can model:

```text
Themes
Concepts
Materials
Techniques
Processes
Visual Language
Research Interests
Interdisciplinary Areas
```

For example:

```text
Medium:
Painting
Sculpture
Installation
Mixed Media

Materials:
Acrylic sheet
Metal
Fabric
Industrial materials

Themes:
Human-technology relationship
Perception
Psychology
Space
Identity
Presence
```

---

# 16. Portfolio Understanding

A major differentiator is allowing the AI to understand the actual portfolio.

The system can process:

- portfolio PDFs
- artwork descriptions
- images
- artist statements
- CV
- exhibition history
- project descriptions

A multimodal model can generate internal representations of:

```text
Artwork
 |
 +-- Medium
 +-- Materials
 +-- Theme
 +-- Style
 +-- Technique
 +-- Concept
 +-- Spatial characteristics
 +-- Technology involvement
```

The system should not replace the artist's interpretation.

It should use the portfolio primarily for **matching and retrieval**.

---

# 17. Opportunity Knowledge Model

Each opportunity should also be represented as a structured knowledge object.

```text
Opportunity
|
+-- Organization
+-- Location
+-- Type
+-- Eligibility
+-- Mediums
+-- Themes
+-- Career Stage
+-- Funding
+-- Duration
+-- Application Requirements
+-- Deadline
+-- Cost
+-- Selection Process
+-- Source
+-- Verification
```

This allows opportunity-to-artist comparison.

---

# 18. Matching Engine

The matching engine has two fundamental stages.

## Stage 1 — Hard Eligibility

Determine whether the artist can apply.

Examples:

```text
Nationality requirement
Age requirement
Location requirement
Career-stage requirement
Education requirement
Medium restriction
Professional experience
Membership requirement
```

Output:

```text
Eligible
Possibly Eligible
Not Eligible
Unknown
```

## Stage 2 — Relevance

If eligible, determine how relevant the opportunity is to the artist.

---

# 19. Matching Score

A possible initial model:

```text
M = wE E + wP P + wD D + wG G + wF F + wT T
```

Where:

- `E` = eligibility compatibility
- `P` = practice/medium compatibility
- `D` = discipline compatibility
- `G` = geographic compatibility
- `F` = funding/preference compatibility
- `T` = thematic compatibility

Example:

```text
Eligibility       25%
Practice          25%
Discipline        20%
Theme             15%
Geography         10%
Funding            5%
```

The weights should be configurable.

---

# 20. Semantic Matching

Keyword matching alone is insufficient.

For example:

```text
Artist:
"explores relationships between technological systems and human perception."

Opportunity:
"seeks artists investigating post-human conditions and emerging technological environments."
```

There may be a strong semantic relationship even though the exact keywords differ.

Therefore the system should use embeddings or semantic representations.

A simplified similarity function:

```text
S_semantic = cosine(E_artist, E_opportunity)
```

where:

- `E_artist` = artist practice embedding
- `E_opportunity` = opportunity description embedding

---

# 21. Hard Rules + AI Reasoning

The system should not rely entirely on an LLM.

Recommended architecture:

```text
              Opportunity
                   |
        +----------+----------+
        |                     |
        v                     v
   Rule Engine             AI Engine
        |                     |
   Hard Eligibility      Semantic Fit
        |                     |
        +----------+----------+
                   |
                   v
             Final Decision
```

Rules should handle objective constraints.

AI should handle semantic interpretation.

This makes the system more reliable and auditable.

---

# 22. Match Explanation

Every recommendation should explain itself.

Example:

> **Match Score: 91/100**
>
> **Why**
>
> - International artists accepted
> - Sculpture and installation explicitly accepted
> - Emerging artists eligible
> - Strong thematic overlap with spatial practice
> - Portfolio-based selection
> - No application fee
>
> **Potential concern**
>
> - Residency requires physical presence for 8 weeks
> - Travel funding is not explicitly stated

This makes recommendations trustworthy.

---

# 23. Deadline Intelligence Engine

Deadline intelligence is one of the core components.

For each opportunity:

```text
days_remaining = deadline - current_time
```

Then classify:

```text
> 90 days       WATCH
61–90 days      PLAN
31–60 days      PREPARE
15–30 days      APPLY SOON
8–14 days       URGENT
1–7 days        FINAL WEEK
< 24 hours      FINAL HOURS
```

These thresholds should be configurable.

---

# 24. Why 30 Days Matters

The system should not simply alert users when a deadline arrives.

Thirty days is useful because many applications require multiple assets.

Example:

```text
Week 1
Research opportunity
Review eligibility
Choose artworks

Week 2
Update portfolio
Update CV
Draft statement

Week 3
Prepare proposal
Collect references
Review requirements

Week 4
Final editing
Upload documents
Submit
```

Therefore:

> **30-day notification = application preparation trigger**

rather than merely a deadline reminder.

---

# 25. Multi-Stage Notifications

The system can support:

```text
60 days
"Opportunity identified."

30 days
"Start preparing."

14 days
"Application window is closing."

7 days
"Final week."

3 days
"Submission preparation required."

24 hours
"Deadline approaching."
```

The artist can customize notification frequency.

---

# 26. Opportunity Priority

Not every opportunity should trigger an alert.

A priority model can combine:

```text
Priority =
Match Score
× Eligibility Confidence
× Opportunity Quality
× Deadline Urgency
× User Preference
```

For example:

```text
HIGH PRIORITY
92 match
30 days remaining

MEDIUM PRIORITY
78 match
72 days remaining

LOW PRIORITY
61 match
120 days remaining
```

This prevents notification overload.

---

# 27. Dashboard

The dashboard could contain:

```text
-------------------------------------------------------
ART OPPORTUNITY INTELLIGENCE
-------------------------------------------------------

TODAY

12 new opportunities
 4 high-match
 5 medium-match
 3 low-match

-------------------------------------------------------

ACTION REQUIRED

3 applications within 30 days

[ Residency A ]     27 days
[ Grant B ]         19 days
[ Exhibition C ]    12 days

-------------------------------------------------------

RECOMMENDED

1. European Sculpture Residency      94%
2. Contemporary Art Grant             91%
3. International Installation Call    87%

-------------------------------------------------------

WATCHLIST

7 opportunities

-------------------------------------------------------

APPLICATIONS

Draft       3
Submitted   5
Waiting     2
Accepted    1
Rejected    2
```

---

# 28. Application Workspace

Each opportunity should have an application workspace.

```text
Opportunity
|
+-- Eligibility
|
+-- Deadline
|
+-- Requirements
|
+-- Portfolio
|
+-- Artist Statement
|
+-- CV
|
+-- Proposal
|
+-- References
|
+-- Budget
|
+-- Submission Link
|
+-- Status
```

This transforms the platform from a discovery tool into an application management system.

---

# 29. Application Status

Possible states:

```text
DISCOVERED
REVIEWING
SHORTLISTED
PREPARING
DRAFT
SUBMITTED
WAITING
INTERVIEW
ACCEPTED
REJECTED
WITHDRAWN
```

---

# 30. Recurring Opportunities

Many opportunities recur annually.

The system should detect recurring patterns.

Example:

```text
2024 — Opened October 4
2025 — Opened October 7
2026 — Opened October 5
```

The system can infer:

> This appears to be an annual opportunity.

But it should clearly label the information:

```text
Confirmed current call: No
Historical recurrence: High
Expected opening period: Early October
```

The system must never turn historical recurrence into a falsely confirmed opportunity.

---

# 31. Opportunity Forecasting

Historical opportunity records can support forecasting.

For example:

```text
Historical Pattern

2022 → October
2023 → October
2024 → September
2025 → October
2026 → October
```

The model can produce:

```text
Expected next cycle:
September–October 2027
Confidence: Medium
```

This gives artists time to prepare before an announcement.

---

# 32. Application Readiness Score

A useful additional metric is:

```text
Readiness = completed_required_assets / total_required_assets
```

Example:

```text
Portfolio          READY
CV                 READY
Artist Statement   READY
Proposal           60%
References         NOT READY

Application Readiness: 68%
```

Then the system can say:

> Deadline in 21 days. Your application is approximately 68% prepared.

---

# 33. Artist Opportunity Graph

A more advanced version can use a knowledge graph.

```text
Artist
 |
 +---- PRACTICES ----> Installation
 |
 +---- USES ---------> Acrylic
 |
 +---- EXPLORES -----> Technology
 |
 +---- EXHIBITED ----> Gallery
 |
 +---- ELIGIBLE FOR -> Residency
 |
 +---- APPLIED TO ---> Grant
 |
 +---- ACCEPTED BY --> Institution
```

Opportunity nodes can connect to:

```text
Organization
Country
Medium
Theme
Artist
Institution
Deadline
Funding
```

This enables graph-based discovery.

---

# 34. Example Knowledge Graph

```text
Artist
  |
  +--> Sculpture
  |       |
  |       +--> Residency A
  |       +--> Grant B
  |
  +--> Installation
  |       |
  |       +--> Biennale C
  |
  +--> Technology
          |
          +--> Fellowship D
```

The system can then discover relationships that keyword search would miss.

---

# 35. Recommendation Engine

The recommendation engine should support several modes.

## Best Match

Highest relevance.

## Best Funding

Strong opportunities with meaningful financial support.

## Best International Exposure

Strong opportunities outside the artist's current region.

## Best Career Development

Opportunities with strong institutional value.

## Easy Wins

High eligibility + strong match + relatively manageable application.

## Stretch Opportunities

More competitive opportunities that could significantly advance the artist's career.

---

# 36. Opportunity Quality Score

A separate score should assess the opportunity itself.

Possible dimensions:

```text
Institutional Reputation
Funding Quality
Career Value
International Reach
Application Cost
Transparency
Historical Credibility
Artist Support
```

This prevents the system from recommending every open call equally.

---

# 37. Scam and Risk Detection

The platform should identify suspicious opportunities.

Potential indicators:

- unclear organizer
- excessive application fee
- unclear selection process
- no official institutional identity
- misleading claims
- inconsistent deadlines
- copied opportunity text
- suspicious payment requirements
- no physical address or legitimate contact
- unusual contractual requirements

The output should be:

```text
LOW RISK
MEDIUM RISK
REVIEW REQUIRED
```

The system should not make defamatory claims. It should state observable reasons.

---

# 38. Source Confidence

Every field can carry confidence.

Example:

```text
Deadline:
Confidence = 0.99

Funding:
Confidence = 0.72

International eligibility:
Confidence = 0.93
```

This allows uncertainty-aware recommendations.

---

# 39. AI Architecture

A practical architecture can use relatively small models for routine tasks and larger models only when necessary.

```text
             Raw Opportunity
                    |
                    v
            Small NLP Model
                    |
          Basic classification
                    |
                    v
          Structured Extraction
                    |
                    v
        Rule / Validation Engine
                    |
                    v
         Embedding Model
                    |
                    v
          Semantic Matching
                    |
                    v
       Larger LLM if ambiguous
                    |
                    v
          Final Recommendation
```

This reduces inference costs.

---

# 40. Recommended Model Roles

## Embedding Model

Used for:

- semantic similarity
- opportunity retrieval
- artist-practice matching

## Small Classification Model

Used for:

- opportunity type
- medium classification
- language classification
- deadline extraction support

## LLM

Used for:

- complex eligibility reasoning
- ambiguous interpretation
- explanation generation
- summarization

## Vision-Language Model

Used for:

- artwork image understanding
- portfolio categorization
- visual similarity
- medium recognition support

---

# 41. Model Independence

The architecture should avoid locking the platform to one AI provider.

Use an abstraction:

```text
AIProvider
|
+-- OpenAI
+-- Anthropic
+-- Gemini
+-- Qwen
+-- Llama
+-- Local Models
```

This supports:

- cost optimization
- privacy
- local inference
- experimentation
- open-source deployment

---

# 42. Open-Source Architecture

A strong open-source implementation could use:

```text
Frontend
React / Vite

Backend
Python / FastAPI

Database
PostgreSQL

Vector Database
pgvector

Task Queue
Celery / Redis

Crawler
Python

Parsing
BeautifulSoup
Playwright
PDF extraction
OCR

AI
Transformers
Sentence Transformers
Open-source LLMs

Deployment
Docker

Monitoring
Prometheus / Grafana
```

---

# 43. Suggested Python Architecture

```text
art-opportunity-intelligence/
|
+-- backend/
|   +-- api/
|   +-- auth/
|   +-- opportunities/
|   +-- artists/
|   +-- applications/
|   +-- matching/
|   +-- notifications/
|
+-- discovery/
|   +-- crawlers/
|   +-- search/
|   +-- feeds/
|   +-- source_registry/
|
+-- extraction/
|   +-- html_parser/
|   +-- pdf_parser/
|   +-- ocr/
|   +-- llm_extractor/
|
+-- matching/
|   +-- eligibility/
|   +-- embeddings/
|   +-- ranking/
|   +-- explanations/
|
+-- monitoring/
|   +-- deadline_monitor/
|   +-- source_monitor/
|   +-- recurrence/
|
+-- models/
|
+-- database/
|
+-- tests/
|
+-- configs/
|
+-- docker/
|
+-- docs/
```

---

# 44. Database Design

Core tables:

```text
artists
artist_practices
artist_artworks
artist_exhibitions
artist_preferences

organizations
sources

opportunities
opportunity_eligibility
opportunity_requirements
opportunity_funding

opportunity_embeddings
artist_embeddings

matches
match_explanations

applications
application_assets
application_events

notifications
deadline_events

source_checks
opportunity_versions
```

---

# 45. Example Opportunity Table

```text
opportunities

id
title
organization_id
type
country
city
description
deadline_date
deadline_time
deadline_timezone
application_fee
status
verification_status
source_url
first_seen
last_seen
last_verified
created_at
updated_at
```

---

# 46. Versioning

Opportunity information changes.

For example:

```text
Original deadline:
30 November

Updated deadline:
15 December
```

The system should retain both states.

```text
Opportunity Version 1
Deadline: Nov 30

Opportunity Version 2
Deadline: Dec 15
```

This creates an audit trail.

---

# 47. Data Pipeline

The discovery pipeline could operate like:

```text
SOURCE DISCOVERY
      ↓
FETCH
      ↓
CONTENT EXTRACTION
      ↓
LANGUAGE DETECTION
      ↓
OPPORTUNITY DETECTION
      ↓
STRUCTURED EXTRACTION
      ↓
NORMALIZATION
      ↓
DUPLICATE DETECTION
      ↓
VALIDATION
      ↓
DATABASE
      ↓
EMBEDDING
      ↓
MATCHING
      ↓
RANKING
      ↓
NOTIFICATION
```

---

# 48. Incremental Updating

The system should not repeatedly process entire websites.

Use:

```text
Last Modified
ETag
Content Hash
URL Hash
Page Fingerprint
```

If nothing changed:

```text
SKIP
```

If changed:

```text
REPROCESS
```

This dramatically reduces compute and crawling costs.

---

# 49. Opportunity Lifecycle

Every opportunity should have a lifecycle.

```text
DISCOVERED
    ↓
PARSED
    ↓
VALIDATED
    ↓
OPEN
    ↓
CLOSING SOON
    ↓
CLOSED
    ↓
ARCHIVED
```

If the source disappears:

```text
SOURCE REMOVED
```

should be recorded rather than silently deleting the opportunity.

---

# 50. Notification System

Notification channels could include:

- email
- web dashboard
- mobile push
- Telegram
- Discord
- calendar integration

Example:

> **AOIS — 30-Day Application Alert**
>
> International Installation Residency
>
> Deadline: November 4, 2026
> Time remaining: 31 days
> Match: 94%
>
> Recommended action:
> Start preparing your proposal.

---

# 51. Calendar Integration

Applications can be automatically converted into calendar milestones.

Example:

```text
Oct 5
Research opportunity

Oct 10
Select portfolio works

Oct 15
Draft statement

Oct 20
Draft proposal

Oct 25
Final review

Nov 1
Submit

Nov 4
Deadline
```

The AI should generate these as suggestions, not silently create commitments.

---

# 52. Personal Application Assistant

Once an artist selects an opportunity, the system can generate a preparation checklist.

For example:

```text
APPLICATION CHECKLIST

[✓] CV
[✓] Portfolio
[ ] Artist statement
[ ] Project proposal
[ ] Budget
[ ] Reference letter
[ ] High-resolution artwork images
```

It can identify missing assets and explain what each requirement means.

---

# 53. Portfolio Relevance

The system can suggest which existing artworks are most relevant to an opportunity.

For example:

```text
Opportunity:
Technology + Installation

Portfolio match:

Artwork A    94%
Artwork B    89%
Artwork C    72%
Artwork D    41%
```

The artist remains the final decision-maker.

The AI should not automatically submit or alter an artist's work.

---

# 54. Application Drafting Assistance

The platform could assist with:

- artist statements
- project proposals
- residency proposals
- cover letters
- biographies
- project descriptions

However, the system should preserve the artist's voice and clearly distinguish:

```text
Artist-authored
AI-assisted
AI-generated draft
```

---

# 55. Application Learning Loop

After an application is submitted:

```text
Application
    ↓
Outcome
    ↓
Accepted / Rejected / Waitlisted
    ↓
Store Outcome
    ↓
Analyze
    ↓
Improve Recommendations
```

The system could eventually identify patterns such as:

> Opportunities emphasizing installation and spatial research appear to be stronger matches than opportunities focused exclusively on traditional painting.

This is not a guarantee of future success; it is personalized evidence from the artist's historical application data.

---

# 56. Feedback Loop

A user should be able to label recommendations:

```text
Excellent Match
Relevant
Not Relevant
Not Eligible
Already Applied
Not Interested
```

These signals improve future ranking.

---

# 57. Personalization Model

The artist's preferences can be represented as:

```text
P_artist =
{
  preferred_regions,
  preferred_opportunity_types,
  preferred_mediums,
  preferred_themes,
  funding_preferences,
  travel_preferences,
  career_goals,
  deadline_preferences
}
```

Matching becomes:

```text
Opportunity × Artist Preference × Eligibility × Practice
```

---

# 58. Privacy

Artist profiles may contain sensitive professional information.

The system should therefore support:

- encryption
- minimal data collection
- user-controlled deletion
- export of artist data
- private portfolios
- private application history
- optional local inference
- explicit consent for AI processing

The system should never publish an artist's private application information without permission.

---

# 59. Security

Important security areas include:

```text
Authentication
Authorization
Encryption
API security
Rate limiting
Secret management
File scanning
Prompt injection protection
Source sanitization
Webhook verification
```

Web content must be treated as untrusted input.

An opportunity webpage could contain malicious instructions intended to manipulate an AI system.

Therefore:

> **Web content must never be allowed to redefine system instructions or application logic.**

---

# 60. Prompt Injection Protection

The extraction architecture should isolate source content.

Conceptually:

```text
SYSTEM INSTRUCTIONS
       |
       | protected
       v
EXTRACTION MODEL
       ^
       |
UNTRUSTED WEB CONTENT
```

The model should extract facts from the content rather than obey instructions embedded within it.

---

# 61. Multilingual Opportunities

The global art ecosystem is multilingual.

The system should eventually support:

- English
- French
- German
- Spanish
- Italian
- Portuguese
- Japanese
- Korean
- Chinese
- Arabic
- Hindi
- Tamil

The internal schema remains language-independent.

---

# 62. Time Zone Handling

Deadlines are not simply dates.

A source may specify:

```text
23:59 CET
23:59 GMT
11:59 PM EST
```

The system should normalize to UTC internally while preserving the original timezone.

```text
deadline_original
deadline_timezone
deadline_utc
```

This prevents false deadline alerts.

---

# 63. Data Quality Metrics

The platform should measure:

```text
Deadline extraction accuracy
Eligibility extraction accuracy
Duplicate detection precision
Source freshness
Match precision
False positive rate
False negative rate
Notification success rate
```

---

# 64. Evaluation Framework

A test dataset should be manually annotated.

For example:

```text
1,000 opportunities
|
+-- Deadline labels
+-- Eligibility labels
+-- Medium labels
+-- Funding labels
+-- Opportunity types
+-- Artist-match labels
```

Evaluate:

### Extraction

Precision / Recall / F1

### Matching

Precision@K  
Recall@K  
NDCG

### Deadline

Absolute date accuracy

### Duplicate Detection

Precision / Recall

---

# 65. Human-in-the-Loop

The system should include HITL for uncertain cases.

Example:

```text
AI confidence < threshold
             |
             v
       HUMAN REVIEW
             |
             v
        Corrected Data
             |
             v
          Database
```

Human review can focus on:

- ambiguous eligibility
- unclear deadlines
- suspicious sources
- funding interpretation
- duplicate conflicts

---

# 66. Confidence-Aware Decisions

Every major AI decision should carry confidence.

Example:

```text
Eligibility:
HIGH

Medium Match:
HIGH

Funding:
MEDIUM

Deadline:
HIGH
```

If confidence is low:

> Information requires verification from the official source.

---

# 67. Source Change Detection

The system should monitor important opportunities after discovery.

If a source changes:

```text
Previous:
Deadline = Nov 30

New:
Deadline = Dec 15
```

The system sends:

> **Deadline changed**

This is especially important for active applications.

---

# 68. Opportunity Change Alerts

Other changes may include:

- deadline extension
- eligibility update
- fee change
- funding update
- application portal closure
- residency duration change
- additional requirement

The artist should be notified only when the change is materially relevant.

---

# 69. User Interface Principles

The interface should prioritize:

1. Action
2. Deadline
3. Eligibility
4. Relevance
5. Explanation

Avoid presenting hundreds of cards without prioritization.

A good opportunity card should look approximately like:

```text
-------------------------------------------------
International Sculpture Residency

MATCH: 94%             27 DAYS LEFT

London, UK
Residency | International

Funding:
Studio + Accommodation

Accepted:
Sculpture | Installation | Mixed Media

Why it matches:
Strong spatial and interdisciplinary overlap.

Requirements:
Portfolio | CV | Statement | Proposal

[VIEW OPPORTUNITY] [SAVE] [START APPLICATION]
-------------------------------------------------
```

---

# 70. Search

Users should be able to search naturally.

Examples:

> Find fully funded sculpture residencies in Europe.

> Show international opportunities with no application fee.

> Find opportunities for emerging installation artists.

> Show opportunities closing within 45 days.

> Find grants supporting experimental art.

Natural-language search can translate into structured filters.

---

# 71. Advanced Query Engine

Example:

```text
"Find fully funded European residencies for emerging
installation artists with deadlines after January 2027."
```

The system extracts:

```text
type = residency
funding = fully funded
region = Europe
career_stage = emerging
medium = installation
deadline > 2027-01-01
```

---

# 72. Opportunity Ranking

A possible ranking function:

```text
R(o,a) =
αM
+ βQ
+ γU
+ δF
+ εC
- ζRisk
```

Where:

- `M` = artist match
- `Q` = opportunity quality
- `U` = urgency
- `F` = funding attractiveness
- `C` = career relevance
- `Risk` = uncertainty or suspicious characteristics

The weights should be configurable.

---

# 73. Competitive Intelligence

The system could eventually analyze the opportunity ecosystem itself.

For example:

```text
Countries with highest number of residencies

Mediums most frequently requested

Average application fees

Typical residency duration

Average funding

Seasonal deadline patterns

Most common application requirements
```

This creates an **Art Opportunity Observatory**.

---

# 74. Art Ecosystem Analytics

Aggregated anonymous data could reveal:

```text
2026 Opportunity Trends

Installation opportunities     +18%
Digital art calls             +24%
Traditional painting          +4%
AI art opportunities          +39%
International residencies     +12%
```

Such analytics could become useful to researchers, institutions, and artists.

Any public analytics should be based on appropriate aggregation and privacy controls.

---

# 75. Research Potential

AOIS is also a research platform.

Possible research areas include:

## AI for Creative Opportunity Discovery

How semantic models can map artists to opportunities.

## Temporal Opportunity Intelligence

Predicting recurring opportunity cycles.

## Human-AI Career Decision Support

How AI recommendations affect artist decision-making.

## Explainable Recommendation Systems

Why an artist receives a recommendation.

## Multimodal Artist Representation

Combining:

- image
- text
- CV
- practice
- exhibition history

into an artist representation.

---

# 76. Possible Novel Research Model

An advanced research direction could define an **Artist Opportunity Representation (AOR)**.

Let:

```text
A = artist representation
O = opportunity representation
```

Then:

```text
A = f(
    portfolio,
    practice,
    biography,
    exhibitions,
    preferences
)
```

and:

```text
O = g(
    requirements,
    themes,
    medium,
    eligibility,
    funding,
    location
)
```

The compatibility function becomes:

```text
C(A,O) = similarity(A,O)
```

with eligibility constraints:

```text
C*(A,O) =
C(A,O), if Eligible(A,O)=1
0,      otherwise
```

This creates a constrained semantic recommendation problem.

---

# 77. Temporal Opportunity Matching

Opportunity relevance is not static.

Define:

```text
T(o,t) = temporal urgency of opportunity o at time t
```

A ranking model can then become:

```text
R(A,O,t)
=
Match(A,O)
× Quality(O)
× T(O,t)
```

As the deadline approaches, the opportunity becomes more actionable.

This allows the system to prioritize:

> **Not only what is relevant, but what is relevant now.**

---

# 78. Opportunity Lifecycle Intelligence

A richer representation is:

```text
Opportunity State
=
Discovery
+
Eligibility
+
Relevance
+
Deadline
+
Preparation
+
Submission
+
Outcome
```

Therefore AOIS becomes a temporal decision-support system rather than a static directory.

---

# 79. Example End-to-End Scenario

Suppose an artist has:

```text
Practice:
Installation + Sculpture

Themes:
Technology + Human Perception

Career:
Emerging

Location:
India

Goal:
International residency
```

The system discovers 1,000 opportunities.

After filtering:

```text
1,000 discovered
 ↓
620 valid opportunities
 ↓
310 potentially eligible
 ↓
120 eligible
 ↓
47 strong practice matches
 ↓
12 high-value opportunities
 ↓
4 urgent opportunities
```

The dashboard shows:

```text
4 ACTIONABLE OPPORTUNITIES

1. Residency A
94% match
28 days

2. Grant B
91% match
21 days

3. Exhibition C
88% match
16 days

4. Fellowship D
86% match
9 days
```

This is the central value proposition.

---

# 80. MVP

The first version should deliberately be small.

## MVP Features

### Artist

- profile
- disciplines
- mediums
- themes
- location
- career stage
- portfolio upload

### Opportunity

- title
- organization
- type
- location
- deadline
- eligibility
- requirements
- funding
- source URL

### AI

- extraction
- classification
- eligibility
- semantic matching
- explanation

### Monitoring

- daily source refresh
- deadline calculation
- 30-day alert

### Interface

- dashboard
- opportunity cards
- saved opportunities

---

# 81. MVP Technology Stack

```text
Frontend
React + Vite + Tailwind

Backend
Python + FastAPI

Database
PostgreSQL

Vector Search
pgvector

Crawler
Python + Playwright

Parsing
BeautifulSoup
PyMuPDF
OCR

AI
Embedding model
Small classifier
LLM

Task Scheduling
Celery + Redis

Deployment
Docker
```

---

# 82. Phase 1

## Foundation

Build:

- database
- artist profile
- opportunity schema
- source registry
- basic crawler
- manual source configuration

Goal:

> Collect and store structured opportunities.

---

# 83. Phase 2

## AI Extraction

Implement:

- deadline extraction
- eligibility extraction
- opportunity classification
- funding extraction
- requirement extraction

Goal:

> Turn unstructured opportunity pages into structured records.

---

# 84. Phase 3

## Matching

Implement:

- artist embeddings
- opportunity embeddings
- hard eligibility rules
- semantic matching
- match score
- explanations

Goal:

> Determine which opportunities matter to a particular artist.

---

# 85. Phase 4

## Deadline Intelligence

Implement:

- 60-day notification
- 30-day notification
- 14-day notification
- 7-day notification
- deadline-change detection

Goal:

> Turn discovery into action.

---

# 86. Phase 5

## Application Workspace

Implement:

- application status
- checklist
- portfolio assets
- proposal
- statement
- CV
- submission tracking

Goal:

> Help artists move from discovery to submission.

---

# 87. Phase 6

## Learning System

Implement:

- application outcomes
- feedback
- personalized ranking
- recommendation learning

Goal:

> Improve recommendations over time.

---

# 88. Phase 7

## Multi-Artist Platform

Implement:

- user accounts
- separate profiles
- privacy controls
- subscriptions if desired
- organization accounts
- opportunity publishing

Goal:

> Turn the personal system into a platform.

---

# 89. Development Roadmap

```text
MONTH 1
Database + backend + source registry

MONTH 2
Discovery + extraction

MONTH 3
AI matching

MONTH 4
Deadline intelligence

MONTH 5
Dashboard + application workspace

MONTH 6
Evaluation + beta

MONTH 7+
Advanced matching + graph + forecasting
```

Actual development time will depend heavily on source integration and the number of websites supported.

---

# 90. Cost Optimization

The system should avoid sending every page to an expensive LLM.

Recommended strategy:

```text
Cheap filtering
      ↓
Small NLP model
      ↓
Rule engine
      ↓
Embedding search
      ↓
LLM only for ambiguity
```

This can substantially reduce inference cost.

Caching should also be used.

---

# 91. Open-Source Strategy

A community version could expose:

```text
Core schemas
Crawler framework
Opportunity parser
Matching engine
Database schema
Evaluation dataset
API
Frontend
```

Sensitive user data remains private.

This could allow researchers and developers to contribute new:

- source connectors
- matching models
- parsers
- language support
- evaluation datasets

---

# 92. Potential Product Names

Possible names:

- ArtOpportunity AI
- ArtCall Intelligence
- ArtScout
- OpenCall Intelligence
- ArtSignal
- ArtRadar
- ArtOrbit
- ArtFlow
- ArtMatch
- ArtPulse
- ArtScope
- Opportunity for Art
- Art Nexus
- Artist Opportunity Intelligence

A more research-oriented name could be:

> **Artist Opportunity Intelligence (AOI)**

A product-oriented name could be:

> **ArtSignal**

---

# 93. Relationship to Open Thought Research

This concept can also fit naturally into a broader AI research ecosystem such as **Open Thought Research**.

Possible research themes:

```text
Open Thought Research
|
+-- AI Systems
|
+-- Human-AI Interaction
|
+-- AI Governance
|
+-- Decision Intelligence
|
+-- Creative Intelligence
|      |
|      +-- Artist Opportunity Intelligence
|
+-- Recommendation Systems
|
+-- Temporal Intelligence
|
+-- Human-Centered AI
```

The project could therefore function both as:

1. an open-source product
2. an applied AI research platform

---

# 94. Potential Research Papers

Possible paper directions include:

### Paper 1

**Artist Opportunity Intelligence: A Semantic and Temporal Recommendation Framework for Creative Professionals**

### Paper 2

**Multimodal Representation of Artists for Opportunity Matching**

### Paper 3

**Temporal Recommendation Systems for Deadline-Driven Creative Opportunities**

### Paper 4

**Explainable AI for Artist Career Opportunity Recommendation**

### Paper 5

**Human-in-the-Loop Opportunity Intelligence for Creative Careers**

---

# 95. Ethical Design

The system should not attempt to decide:

> "You should apply for this because you will win."

Instead:

> "This opportunity appears relevant based on the available information."

The artist remains responsible for the decision.

The system should also avoid reinforcing narrow career definitions.

An artist may intentionally pursue an opportunity outside their established practice.

Therefore users should be able to override recommendations.

---

# 96. Avoiding Algorithmic Bias

Recommendation systems can develop bias toward:

- famous institutions
- Western opportunities
- English-language sources
- highly represented mediums
- artists with extensive documentation

The system should explicitly monitor these biases.

Potential corrective mechanisms:

- source diversity
- geographic diversity
- multilingual indexing
- new-organization discovery
- transparent scoring
- user-controlled ranking
- diversity-aware recommendations

---

# 97. Human Agency

The system should be designed as:

```text
AI recommends
Artist decides
```

not:

```text
AI decides
Artist follows
```

This distinction should be fundamental to the product.

---

# 98. Long-Term Vision

The ultimate system could become a global **Creative Opportunity Graph**.

```text
                    ARTISTS
                       |
              +--------+--------+
              |                 |
          PRACTICES         CAREERS
              |                 |
              +--------+--------+
                       |
                  OPPORTUNITIES
                       |
        +--------------+--------------+
        |              |              |
    RESIDENCIES      GRANTS       EXHIBITIONS
        |              |              |
        +--------------+--------------+
                       |
                 INSTITUTIONS
                       |
             COUNTRIES / CITIES
                       |
                  ART ECOSYSTEM
```

The graph could become a structured map of the global art opportunity ecosystem.

---

# 99. Future Capabilities

Possible future capabilities include:

- artist-to-opportunity recommendation
- opportunity-to-artist discovery
- collaboration matching
- curator discovery
- institution discovery
- recurring opportunity prediction
- grant trend analysis
- art ecosystem analytics
- application portfolio optimization
- personalized career planning
- opportunity calendars
- multilingual discovery
- mobile application
- browser extension
- email opportunity ingestion
- newsletter parsing
- personal opportunity inbox

---

# 100. Browser Extension Concept

An artist browsing a webpage could click:

> **Analyze with AOIS**

The extension extracts the opportunity and shows:

```text
MATCH: 92%

Eligible: YES

Deadline: 42 days

Why:
Strong match with installation practice.

Application difficulty:
Medium

Funding:
Accommodation provided

[ADD TO AOIS]
```

This would make the platform useful even when the opportunity is not discovered by the central crawler.

---

# 101. Email Intelligence

Artists often receive opportunities through newsletters.

The system could provide an optional:

> **Opportunity Inbox**

The artist forwards an email.

AOIS extracts:

```text
Opportunity
Deadline
Eligibility
Requirements
Funding
Source
```

and adds it to the personal database.

---

# 102. Opportunity Calendar

The system could automatically generate:

```text
OCTOBER
4 opportunities

NOVEMBER
8 opportunities

DECEMBER
12 opportunities

JANUARY
5 opportunities
```

Artists can visually identify busy application periods.

---

# 103. Opportunity Portfolio

The system could maintain a personal history:

```text
Applications 2026

Submitted: 18
Accepted: 3
Rejected: 9
Waiting: 6

Acceptance Rate:
16.7%
```

This data should be treated as personal analytics rather than a universal measure of artistic quality.

---

# 104. Personal Career Intelligence

Eventually, AOIS could answer:

> What types of opportunities am I pursuing?

> Which countries am I applying to?

> Which application types have produced responses?

> Which requirements repeatedly slow me down?

> Which documents should I prepare in advance?

This turns the system into a **career operations assistant for artists**.

---

# 105. Reusable Application Assets

The system can maintain reusable versions of:

```text
CV
Short Bio
Long Bio
Artist Statement
Practice Statement
Portfolio
Project Descriptions
Artwork Metadata
Biography
Headshot
References
```

When a new opportunity arrives:

```text
Opportunity Requirements
        ↓
Required Assets
        ↓
Existing Artist Assets
        ↓
Missing Assets
        ↓
Preparation Plan
```

---

# 106. Opportunity-to-Portfolio Matching

An advanced multimodal model can compare:

```text
Opportunity Theme
        +
Opportunity Medium
        +
Opportunity Curatorial Context
```

against:

```text
Portfolio Artwork
        +
Artwork Description
        +
Artist Practice
```

This can produce:

```text
Portfolio relevance

Artwork 01     95
Artwork 07     92
Artwork 03     86
Artwork 12     71
```

The artist chooses which works to submit.

---

# 107. Application Optimization Without Fabrication

The system can help organize an application but should never invent:

- exhibitions
- awards
- qualifications
- artwork facts
- professional relationships
- experience

All factual claims should trace back to the artist's supplied information.

---

# 108. Data Provenance

Every important extracted fact should be traceable.

Example:

```text
Deadline
|
+-- Source URL
+-- Source page
+-- Extraction timestamp
+-- Model
+-- Confidence
```

This makes the system auditable.

---

# 109. Auditability

A user should be able to ask:

> Why did you say I am eligible?

The system should answer:

```text
Opportunity states:
International artists accepted.

Your profile states:
Artist based in India.

No nationality restriction detected.

Conclusion:
Eligible, subject to final verification.
```

This is preferable to an opaque percentage.

---

# 110. Failure Modes

The system should explicitly handle:

### Missing Deadline

```text
Deadline unknown
```

### Ambiguous Eligibility

```text
Eligibility requires verification
```

### Conflicting Sources

```text
Official source and directory disagree.
Official source prioritized.
```

### Expired Opportunity

```text
Closed
```

### Source Removed

```text
No longer verified
```

### Duplicate

```text
Merged with canonical opportunity
```

---

# 111. Reliability Principle

The platform should follow:

> **Unknown is better than invented.**

This should be a core engineering principle.

If the system cannot determine something reliably, it should surface uncertainty.

---

# 112. Example Daily Workflow

Every morning:

```text
06:00
Source discovery

06:30
New content extraction

07:00
AI classification

07:30
Validation

08:00
Matching

08:30
Deadline evaluation

09:00
Notification generation
```

The exact schedule is configurable.

---

# 113. Example Alert

```text
ART OPPORTUNITY ALERT

European Contemporary Art Residency

MATCH: 93%
PRIORITY: HIGH

Deadline:
30 October 2026

Time remaining:
26 days

Location:
Berlin, Germany

Eligibility:
International emerging artists

Relevant practices:
Installation
Sculpture
Mixed Media

Funding:
Studio provided
Accommodation provided
Travel not specified

Application:
Portfolio
CV
Artist Statement
Project Proposal

Why this matters:
Strong match with your spatial and interdisciplinary
practice.

Recommended action:
Begin proposal preparation.

[VIEW OFFICIAL SOURCE]
[ADD TO APPLICATIONS]
```

---

# 114. Success Metrics

The project should not measure success only by number of opportunities collected.

Better metrics include:

```text
Opportunity discovery coverage
Relevant opportunities per artist
False recommendation rate
Deadline accuracy
Alert usefulness
Application completion rate
Application submission rate
User retention
Artist feedback
Time saved per artist
```

A key product metric could be:

> **Actionable Opportunities per Artist per Month**

rather than:

> Total opportunities in database.

---

# 115. MVP Success Criterion

A strong MVP should answer:

> Can the system save an artist several hours of weekly opportunity searching while surfacing opportunities they would realistically consider applying to?

If yes, the core product has value.

---

# 116. Final Architecture

The complete conceptual system is:

```text
                         GLOBAL WEB
                             |
         +-------------------+-------------------+
         |                   |                   |
     Institutions         Galleries          Foundations
         |                   |                   |
         +-------------------+-------------------+
                             |
                             v
                  OPPORTUNITY DISCOVERY
                             |
                             v
                 CONTENT EXTRACTION / OCR
                             |
                             v
                    AI STRUCTURING
                             |
                             v
                 VALIDATION + PROVENANCE
                             |
                             v
                  OPPORTUNITY KNOWLEDGE
                             |
              +--------------+--------------+
              |                             |
              v                             v
       ARTIST KNOWLEDGE              APPLICATION HISTORY
              |                             |
              +--------------+--------------+
                             |
                             v
                     MATCHING ENGINE
                             |
                  +----------+----------+
                  |                     |
                  v                     v
             ELIGIBILITY           SEMANTIC FIT
                  |                     |
                  +----------+----------+
                             |
                             v
                      RANKING ENGINE
                             |
                             v
                  TEMPORAL INTELLIGENCE
                             |
                             v
                  DEADLINE MONITORING
                             |
             +---------------+---------------+
             |               |               |
             v               v               v
          Dashboard        Email          Mobile
                             |
                             v
                  APPLICATION WORKSPACE
                             |
                             v
                         OUTCOME
                             |
                             v
                       LEARNING LOOP
                             |
                             +------------------+
                                                |
                                                v
                                      IMPROVED MATCHING
```

---

# 117. Conclusion

The **Art Opportunity Intelligence System** is fundamentally a **decision-support and discovery infrastructure for artists**.

Its central innovation is not merely collecting open calls.

It combines:

- continuous opportunity discovery
- structured information extraction
- eligibility reasoning
- multimodal artist representation
- semantic matching
- opportunity quality assessment
- deadline intelligence
- source verification
- application readiness
- personalized recommendations
- application tracking
- outcome-based learning

The most important conceptual shift is:

```text
Traditional Model:

Artist
  ↓
Search
  ↓
Read
  ↓
Filter
  ↓
Remember Deadline
  ↓
Apply


AOIS Model:

Artist Profile
  ↓
Continuous Intelligence
  ↓
Opportunity Discovery
  ↓
Eligibility Analysis
  ↓
Practice Matching
  ↓
Priority Ranking
  ↓
Deadline Prediction
  ↓
Preparation Plan
  ↓
Application
  ↓
Outcome
  ↓
Learning
```

This transforms opportunity discovery from a **manual search problem** into an **intelligent temporal recommendation problem**.

The long-term vision is not simply an "open call website."

It is a **Creative Opportunity Intelligence Layer** connecting artists, institutions, funding programmes, residencies, exhibitions, competitions, and the broader global art ecosystem.

The system can begin as a personal tool for one artist, become an open-source research project, and eventually evolve into a global platform for artist opportunity intelligence.

---

# 118. Proposed First Implementation

The recommended first implementation should focus on one artist profile and a controlled set of reliable sources.

### Version 0.1

```text
Python
FastAPI
PostgreSQL
pgvector
React
Playwright
BeautifulSoup
PyMuPDF
Sentence Transformers
LLM
Redis
Celery
Docker
```

### Initial capabilities

```text
[✓] Artist profile
[✓] Opportunity database
[✓] Source registry
[✓] Web discovery
[✓] AI extraction
[✓] Eligibility matching
[✓] Semantic matching
[✓] Match explanations
[✓] Deadline calculation
[✓] 30-day alerts
[✓] Dashboard
[ ] Application workspace
[ ] Outcome learning
[ ] Recurrence prediction
[ ] Opportunity graph
```

This creates a focused and technically achievable foundation while preserving a clear path toward the full platform.

---

# 119. Core Principle

> **Find the opportunity. Understand the opportunity. Understand the artist. Connect the two. Know when to act.**

That is the core of the Art Opportunity Intelligence System.

