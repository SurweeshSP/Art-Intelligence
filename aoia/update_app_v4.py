import os

app_content = """\
import streamlit as st
import json
import yaml
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd

from aoia import pipeline, db

st.set_page_config(page_title="AOIA Dashboard", layout="wide")

# Init DB on first load
db.init_db()

st.sidebar.title("AOIA Settings")

# Demo Data toggle
use_demo = st.sidebar.checkbox("Use Demo Data (Seed Records)", value=False)
if use_demo:
    st.sidebar.warning("DEMO DATA ENABLED")
    st.warning("DEMO DATA ENABLED - Showing seeded records, not live crawl results.")
    db.seed_demo_data()

# Load Profile
try:
    with open("configs/artist_profile.json") as f:
        profile = json.load(f)
except:
    profile = {}

st.sidebar.subheader("Artist Profile")
st.sidebar.text(f"Location: {profile.get('location', {}).get('city')}")
st.sidebar.text(f"Mediums: {', '.join(profile.get('mediums', []))}")

run_status = st.sidebar.empty()
if 'run_state' not in st.session_state:
    st.session_state['run_state'] = "Ready"

run_status.info(f"Status: {st.session_state['run_state']}")

if st.sidebar.button("Run AOIA now", type="primary"):
    st.session_state['run_state'] = "Running..."
    run_status.info(f"Status: {st.session_state['run_state']}")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def cb(msg):
        status_text.text(msg)
        
    ranked_opps, sources, diagnostics = pipeline.run_pipeline(progress_callback=cb)
    st.session_state['ranked'] = ranked_opps
    st.session_state['sources'] = sources
    st.session_state['diagnostics'] = diagnostics
    progress_bar.progress(100)
    status_text.text("Run complete!")
    st.session_state['run_state'] = "Completed"
    run_status.info(f"Status: {st.session_state['run_state']}")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", "Opportunities", "Closing Soon", "New & Changes", "Recently Closed", "Sources"
])

def render_opps_table(opps):
    if not opps:
        st.info("No verified open opportunities found. Run AOIA again or inspect Source Health.")
        return
    df = pd.DataFrame([{
        "Priority": f"{o.priority_score:.2f}" if o.priority_score > 0 else "ERROR",
        "Title": o.title,
        "Provider": o.provider if o.provider != "Extracted Provider" else "Provider not verified",
        "Type": o.type,
        "Location": f"{o.location.city}, {o.location.country}" if o.location.city and o.location.city != "Unknown" else o.geo_scope,
        "Deadline": o.deadline_date if o.deadline_date else "UNKNOWN",
        "Status": o.status,
        "URL": o.application_url
    } for o in opps])
    
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "URL": st.column_config.LinkColumn("Open Link")
        }
    )

with tab1:
    st.header("AOIA Dashboard Overview")
    st.write(f"**Last Run Time (IST):** {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Verified Open", len([o for o in opps if o.status == "OPEN"]))
    col2.metric("High Priority", len([o for o in opps if o.priority_score >= 0.8]))
    col3.metric("Closing <= 7 Days", len([o for o in opps if o.status == "CLOSING_SOON"]))
    col4.metric("New This Run", len([o for o in opps if getattr(o, "first_seen", None) is not None])) # simplified
    sources_checked = len(st.session_state.get('sources', []))
    col5.metric("Sources Checked", sources_checked if sources_checked > 0 else "Not run yet")
    
    diagnostics = st.session_state.get('diagnostics', {})
    if diagnostics:
        with st.expander("Run Diagnostics"):
            st.json(diagnostics)

with tab2:
    st.header("Ranked Opportunities")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    open_opps = sorted([o for o in opps if o.status in ["OPEN", "DEADLINE_UNKNOWN"]], key=lambda x: -x.priority_score)
    render_opps_table(open_opps)

with tab3:
    st.header("Closing Soon")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    closing_opps = [o for o in opps if o.status == "CLOSING_SOON" and o.deadline_date != "UNKNOWN"]
    render_opps_table(closing_opps)
    
with tab4:
    st.header("New & Changes")
    st.info("New opportunities and material changes will appear here.")

with tab5:
    st.header("Recently Closed")
    opps = st.session_state.get('ranked', db.load_all_opportunities())
    closed_opps = [o for o in opps if o.status == "RECENTLY_CLOSED"]
    render_opps_table(closed_opps)

with tab6:
    st.header("Source Health")
    sources = st.session_state.get('sources', [])
    if sources:
        df = pd.DataFrame([{
            "Name": s['name'],
            "URL": s['base_url'],
            "Tier": s['authority_tier'],
            "Status": s.get('verification', 'PENDING'),
            "Reason": s.get('health_reason', '')
        } for s in sources])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Run the pipeline to check sources.")
"""

with open("aoia/app.py", "w", encoding="utf-8") as f:
    f.write(app_content)
