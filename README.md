# Art-Intelligence

**Art Opportunity Intelligence Agent (AOIA)** — An automated discovery, verification, and ranking engine for visual and fine arts opportunities (fellowships, open calls, residencies, grants).

## Features
- **Curated Opportunity Dashboard**: Powered by Streamlit with real-time filtering by medium, geo-scope, and deadline.
- **Automated Daily Crawling**: GitHub Actions crawler scheduled daily at 06:00 AM IST to monitor and update verified opportunities.
- **Zero-Lag Streamlit Cloud Deployment**: Serves pre-indexed, verified opportunities directly from SQLite.

## Running Locally
```bash
pip install -r requirements.txt
streamlit run aoia/app.py
```

## Running Crawler Manually
```bash
python run_crawler.py
```
