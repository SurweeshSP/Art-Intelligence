# AOIA — Art Opportunity Intelligence Agent

AOIA is an intelligent discovery, verification, and ranking engine specifically tailored for **fine-arts opportunities** (painting, drawing, sculpture, printmaking, ceramics, installation, mixed media, textile/fibre, mural/public art, collage, video art).

---

## 1. Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Validate Sources Registry
```bash
python validate_sources.py configs/sources.yaml
```

### Run Tests
```bash
python -m pytest -q
```

### Run the Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 2. Configuring Search API Keys
AOIA supports web discovery for unresolved sources and dynamic fine-arts open calls:
1. Set environment variable:
   ```bash
   export BRAVE_API_KEY="your-api-key-here"
   ```
2. Or configure via `.streamlit/secrets.toml`:
   ```toml
   BRAVE_API_KEY = "your-api-key-here"
   ```

---

## 3. How to Add a New Source to Registry v4

1. Open `configs/sources.yaml`.
2. Add a new source block to the `sources:` list adhering strictly to the registry schema:
```yaml
  - source_id: unique_source_slug
    name: Organisation / Grant Name
    region: chennai        # chennai | india | international
    authority_tier: T0     # T0 | T1 | T2 | T3 | T4
    base_url: https://official-art-provider.org/
    source_type: museum    # museum | gallery | foundation | government | platform
    channel_role: organiser # organiser | funder | venue | sales | discovery
    fine_arts_fit: HIGH    # HIGH | MED | LOW
    geo_basis: registry    # registry (own site) | text (directory/media)
    country: IN            # ISO-2 country code
    city: Chennai
    enabled: true
    verification: PENDING  # Always begins PENDING
    origin: user_list
    crawl_interval_minutes: 720
    priority: 85
    career_level:
      - any
```
3. Run `python validate_sources.py configs/sources.yaml` to ensure zero schema errors before committing.

---

## 4. Automated Daily Crawl (GitHub Actions + Streamlit Cloud)
AOIA includes an automated GitHub Actions workflow (`.github/workflows/daily_crawler.yml`):
- Runs every day at 06:00 AM IST (00:30 UTC), or manually via **Actions -> Run workflow**.
- Crawls all active registry sources, scores opportunities, and updates `aoia_data.db`.
- Commits and pushes the updated database back to GitHub.
- Streamlit Cloud automatically picks up the push and refreshes with latest opportunities.
