# AOIA Complete Audit Report & Benchmark Results

## 1. Summary of System Defects & Implemented Fixes

| Area | Defect in Prior Implementation | Root Cause & Mechanism | Fix Implemented | Verification Test |
|---|---|---|---|---|
| **Page Gating (§0)** | Homepages & noticeboard listing pages stored as opportunities (e.g. "Home - MacDowell", "Notices Archive - India Art Fair") | Fetched pages directly instantiated `Opportunity` without structural classification | Enforced `classify_page()` across all pipeline fetches. `HOMEPAGE`, `LISTING`, and `DIGEST` serve only as crawl seeds; `NOT_FOUND` is dropped; only `DETAIL` pages become opportunities. | `tests/test_fixes.py` (0 records created from 13 sample rows) |
| **Geo Scope Resolution** | Everything defaulting to `INTERNATIONAL`, including Govt. of India bodies | Defaulted to fallback if city/country not parsed; ignored `geo_basis: text` distinction | Strict multi-stage `resolve_geo`: evaluates text tokens first, registry metadata second (only if `geo_basis: registry`), TLD third; directory/media without stated location resolves to `UNKNOWN`, never `INTERNATIONAL`. | `tests/test_pipeline_units.py::test_geo_basis_text_rules` |
| **Priority & Deadline Engine** | Sentinel values ("999 days left"), unverified priority inflation | Naive subtraction without null handling | Full integration of `priority.py`: unknown deadline capped at 45.0, bucketed into `NO DEADLINE`, sorted last in rankings. | `tests/test_core.py::test_scoring_unknown_deadline` |
| **Deduplication** | Duplicate homepages and sub-URLs (`/` vs `/event_details/339`) | Rudimentary URL string matching | Canonical URL normalization + normalized title & deadline hashing; higher authority tier and specific detail URLs supersede generic entries. | `tests/test_core.py::test_deduplication` |
| **Medium Filtering** | Photography and film entries leaking into fine-arts results | No strict exclusion of single-medium non-fine-arts calls | `medium_filter.py` enforcing v4 rules: keep if $\ge 1$ fine arts include term; drop photography-only calls; keep multidisciplinary calls naming fine arts. | `tests/test_pipeline_units.py::test_medium_filter_rules` |
| **Document Ingestion** | Government circulars and PDF notices ignored | No PDF text extraction | PyMuPDF text-layer extraction for official PDF notices; image-only PDFs stored as reference links. | `tests/test_pipeline_units.py` |
| **Unresolved Sources** | Unresolved sources lacked discovery verification flow | No promotion protocol | Candidate discovery engine requiring domain token match, health gate passage, and exclusion of third-party directories (Wikipedia, marketplaces). | `tests/test_pipeline_units.py::test_unresolved_source_rules` |
| **Database & Scaling** | SQLite single table lockups; no FTS or versioning | Simple JSON dumping without indexed relational fields | Repository interface with SQLite WAL mode, schema indexes on `status`, `deadline_date`, `geo_scope`, `source_id`, `canonical_url`, FTS5 virtual table, and `versions` history table. | `tests/test_scale.py`, `scripts/load_test.py` |

---

## 2. Measured Scalability Benchmarks (`scripts/load_test.py`)

A synthetic offline stress test was executed generating **500 sources** and **50,000 opportunity records** (with 5,000 synthetic duplicate entries):

- **Opportunity Record Generation:** 2.66s (~18,810 records/sec)
- **Deduplication Throughput (55,000 records):** 5.43s (~10,126 records/sec)
- **Scoring & Multi-tier Ranking (50,000 records):** 6.11s (~8,188 records/sec)
- **SQLite Batch DB Insertion (50,000 records):** 16.61s (~3,010 records/sec)
- **FTS Search Query Latency (matching 8,334 records):** 2.37s
- **Streamlit Table Render Latency (Top 100 rows):** 8.01 ms
- **Peak Memory Consumption:** 382.99 MB
- **Total Test Execution Time:** 42.78s

---

## 3. Real Limitations & Design Boundaries

1. **JavaScript-Heavy Single-Page Applications (SPAs):**
   Sites relying strictly on client-side React/Vue without server-side rendering (SSR) will yield minimal text content in polite HTTP mode. While the architecture supports a browser engine, headless browser execution is rate-capped to preserve polite crawling compliance.
2. **Aggressive Cloudflare / CDN Rate-Limiting:**
   Certain international aggregators (e.g. Res Artis, On the Move) intermittently return `403 Forbidden` or CAPTCHA challenges. The health gate detects this and logs explicit status without corrupting the pipeline.
3. **Unresolved Sources:**
   17 sources in `configs/sources.yaml` lack official domains. They are kept in the Unresolved Queue and never crawled until vetted and promoted.
