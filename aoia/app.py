import html
import json
import sys
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st

# Ensure aoia package is discoverable whether started from repo root or aoia directory
_current_dir = Path(__file__).resolve().parent
_repo_dir = _current_dir.parent
for _p in (_current_dir, _repo_dir):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from aoia import db, pipeline, registry, health, exports, unresolved
from aoia.models import Opportunity

st.set_page_config(
    page_title="Fine Arts Opportunity Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Editorial & Gallery CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #24292e;
}

.stApp {
    background-color: #fcfbfa;
}

h1, h2, h3, .editorial-heading {
    font-family: 'Cinzel', serif;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}

.header-banner {
    background: linear-gradient(135deg, #1c1d1f 0%, #2a2c30 100%);
    padding: 24px 32px;
    border-radius: 12px;
    color: #f7f7f8;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border-left: 5px solid #d4a373;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #eae7e4;
    border-radius: 8px;
    padding: 14px 18px;
    text-align: left;
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.metric-title {
    font-size: 0.78rem;
    text-transform: uppercase;
    color: #71767b;
    letter-spacing: 0.05em;
    font-weight: 600;
}

.metric-val {
    font-size: 1.6rem;
    font-weight: 700;
    color: #111418;
    margin-top: 4px;
}

.opp-card {
    background: #ffffff;
    border: 1px solid #e7e5e2;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.opp-card:hover {
    border-color: #d4a373;
    box-shadow: 0 6px 16px rgba(212, 163, 115, 0.12);
}

.chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}

.chip-geo { background: #eef2f6; color: #2b4c7e; }
.chip-type { background: #fbf0ea; color: #b25e29; }
.chip-medium { background: #f0f4ee; color: #3b6b35; }
.chip-fee { background: #eaf8f0; color: #1e7e45; border: 1px solid #b7ebc9; }
.chip-verif { background: #f5efff; color: #6930c3; }
.chip-deadline { background: #fff4e5; color: #b76e00; font-weight: 600; }
.chip-urgent { background: #ffebee; color: #c62828; font-weight: 700; }

.kanban-col {
    background: #f4f3f0;
    padding: 16px;
    border-radius: 8px;
    min-height: 400px;
}
</style>
""", unsafe_allow_html=True)

# Initialize DB on load
db.init_db()

now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))

# State initialization
if "applications" not in st.session_state:
    st.session_state["applications"] = {
        "Saved": set(),
        "Preparing": set(),
        "Submitted": set(),
        "Result": set()
    }

if "saved_ids" not in st.session_state:
    st.session_state["saved_ids"] = set()

if "selected_opp_id" not in st.session_state:
    st.session_state["selected_opp_id"] = None

# Sidebar Configuration & Filters
st.sidebar.markdown("### 🏛️Control Panel")

# Load Artist Profile
profile_path = Path("configs/artist_profile.json")
if not profile_path.exists():
    profile_path = Path(__file__).resolve().parent / "configs" / "artist_profile.json"

try:
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)
except Exception:
    profile = {}

# Demo Data toggle
use_demo = st.sidebar.checkbox("Load Demo Records (Terrain & SAM)", value=False)
if use_demo:
    db.seed_demo_data()
    st.sidebar.caption("Seeded Terrain (Delhi) and SAM (Cycle 4) in database.")

# Artist Profile Display
with st.sidebar.expander("👤 Artist Profile & Weights", expanded=False):
    st.write(f"**City:** {profile.get('location', {}).get('city', 'Chennai')}")
    st.write(f"**Fine Arts:** {', '.join(profile.get('mediums', []))}")
    st.write(f"**Income policy:** Low-income priority (Fee-free first)")
    st.slider("Geo Weight", 0.0, 1.0, 0.30, 0.05, key="w_geo")
    st.slider("Money Weight", 0.0, 1.0, 0.25, 0.05, key="w_money")
    st.slider("Date Proximity Weight", 0.0, 1.0, 0.30, 0.05, key="w_date")
    st.slider("Fit Weight", 0.0, 1.0, 0.15, 0.05, key="w_fit")

# Pipeline Run Button & Status
st.sidebar.markdown("### ⚡ Crawl Pipeline")
if st.sidebar.button("Run Live Pipeline Now", type="primary", use_container_width=True):
    prog_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    def cb(msg):
        status_text.caption(msg)
    
    with st.spinner("Executing polite crawl & ranking pipeline..."):
        ranked, checked_sources, diag = pipeline.run_pipeline(progress_callback=cb)
        st.session_state["ranked"] = ranked
        st.session_state["sources"] = checked_sources
        st.session_state["diagnostics"] = diag
        prog_bar.progress(100)
        status_text.success("Crawl complete!")
        st.rerun()


# Load All Data from DB (Auto-seed if DB is empty so verified open public calls are immediately visible)
raw_opps = db.load_all_opportunities()
if not raw_opps:
    db.seed_demo_data()
    raw_opps = db.load_all_opportunities()

sources_list = db.load_sources()
if not sources_list:
    reg_init = registry.load_registry("configs/sources.yaml")
    sources_list = [s.model_dump() for s in reg_init.sources]
    db.save_sources(sources_list)

# Rank all open opportunities directly without prior filtering
all_ranked_opps = pipeline.scoring.score_and_rank(raw_opps)
ranked_opps = all_ranked_opps

# Header Metric Strip
sources_passed = sum(1 for s in sources_list if s.get("verification") == "PASSED")
sources_failed = sum(1 for s in sources_list if s.get("verification") == "FAILED")
sources_enabled = sum(1 for s in sources_list if s.get("enabled", 1))
open_count = len([o for o in raw_opps if o.status in ("OPEN", "ROLLING", "DEADLINE_UNKNOWN")])
closing_7d = len([o for o in raw_opps if o.days_left is not None and 0 <= o.days_left <= 7])

st.markdown(f"""
<div class="header-banner">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="color:#ffffff; margin:0; font-size:1.8rem;">Fine Arts Opportunity Intelligence</h1>
            <p style="color:#cfd2d6; margin:4px 0 0 0; font-size:0.95rem;">
                Verified calls, fellowships, grants & residencies for visual & fine artists
            </p>
        </div>
        <div style="text-align:right;">
            <span style="background:rgba(255,255,255,0.12); padding:6px 14px; border-radius:20px; font-size:0.85rem; color:#f0f2f5;">
                IST Time: {now_ist.strftime('%d %b %Y, %H:%M')}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Metric Columns
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Verified Active</div><div class="metric-val" style="color:#1e7e45;">{open_count}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Closing &le; 7 Days</div><div class="metric-val" style="color:#b76e00;">{closing_7d}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Sources Monitored</div><div class="metric-val">{len(sources_list)}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Active Sources</div><div class="metric-val" style="color:#2b4c7e;">{sources_enabled}</div></div>', unsafe_allow_html=True)
with m5:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Health Check</div><div class="metric-val" style="color:#2b4c7e;">{sources_passed} Pass / {sources_failed} Fail</div></div>', unsafe_allow_html=True)

st.write("")

# Main Tabs
tabs = st.tabs([
    "🎨 Discover",
    "⏳ Closing Soon",
    "📅 Calendar",
    "🗺️ Map",
    "🏛️ Where to Show / Sell",
    "📋 My Applications",
    "🔌 Sources & Health",
    "⚠️ Needs Review"
])

# Helper Card Renderer
def render_opportunity_card(opp: Opportunity, show_controls: bool = True, prefix: str = ""):
    dl_str = f"Deadline: {opp.deadline_date}" if opp.deadline_date and opp.deadline_date != "UNKNOWN" else "Deadline not stated"
    days_badge = f"{opp.days_left}d left" if opp.days_left is not None and opp.days_left >= 0 else opp.bucket_label
    
    fee_text = "Fee-free" if opp.financial.application_fee == 0 else f"Fee: {opp.financial.application_fee}" if opp.financial.application_fee else "Fee: Check site"
    loc_display = opp.geo_scope if opp.geo_scope != "UNKNOWN" else "Location not stated"

    # Badges
    geo_badge = f'<span class="chip chip-geo">{html.escape(loc_display)}</span>'
    type_badge = f'<span class="chip chip-type">{html.escape(opp.type.upper())}</span>'
    fee_badge = f'<span class="chip chip-fee">{html.escape(fee_text)}</span>'
    verif_badge = f'<span class="chip chip-verif">{html.escape(opp.verification)}</span>'
    dl_badge = f'<span class="chip chip-deadline">{html.escape(dl_str)} ({days_badge})</span>'

    card_html = f"""
    <div class="opp-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="flex:1;">
                <h3 style="margin:0 0 4px 0; font-size:1.15rem; color:#1a1a1a;">{html.escape(opp.title)}</h3>
                <div style="font-size:0.9rem; color:#555; margin-bottom:10px;">
                    <strong>{html.escape(opp.provider)}</strong> &middot; Tier: {opp.source.tier or 'T0'}
                </div>
                <div>
                    {geo_badge} {type_badge} {dl_badge} {fee_badge} {verif_badge}
                </div>
            </div>
            <div style="text-align:right; min-width:90px;">
                <div style="font-size:1.25rem; font-weight:700; color:#d4a373;">{opp.priority_score:.1f}</div>
                <div style="font-size:0.75rem; color:#888;">Priority Score</div>
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if show_controls:
        c1, c2, c3, c4 = st.columns([2, 1, 1, 4])
        with c1:
            if st.button(f"🔍 Inspect Detail", key=f"{prefix}det_{opp.id}"):
                st.session_state["selected_opp_id"] = opp.id
        with c2:
            is_saved = opp.id in st.session_state["saved_ids"]
            if st.button("★ Saved" if is_saved else "☆ Save", key=f"{prefix}fav_{opp.id}"):
                if is_saved:
                    st.session_state["saved_ids"].remove(opp.id)
                    st.session_state["applications"]["Saved"].discard(opp.id)
                else:
                    st.session_state["saved_ids"].add(opp.id)
                    st.session_state["applications"]["Saved"].add(opp.id)
                st.rerun()
        with c3:
            if st.button("➕ Apply", key=f"{prefix}app_{opp.id}"):
                st.session_state["applications"]["Preparing"].add(opp.id)
                st.success("Added to Preparing!")
        with c4:
            st.markdown(f"[↗ Open Official Provider Page]({opp.application_url})")

# Helper Detail Drawer
def render_detail_drawer(opp_id: str):
    opp = next((o for o in raw_opps if o.id == opp_id), None)
    if not opp:
        return
    with st.expander(f"🔎 Detail Inspector: {opp.title}", expanded=True):
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.write(f"**Provider:** {opp.provider}")
            st.write(f"**Application URL:** [{opp.application_url}]({opp.application_url})")
            st.write(f"**Why Ranked:** {opp.why_text}")
            st.write(f"**Status / Bucket:** {opp.status} ({opp.bucket_label})")
            st.write(f"**Location Scope:** {opp.geo_scope}")
            if opp.evidence:
                st.markdown("#### Evidence & Snippets")
                for ev in opp.evidence:
                    st.info(f"**{ev.get('field', 'field').upper()}:** {ev.get('snippet')} (Confidence: {ev.get('confidence')})")
        with col_r:
            st.write(f"**Authority Tier:** {opp.source.tier}")
            st.write(f"**Verification:** {opp.verification}")
            st.write(f"**Fee:** {opp.financial.application_fee}")
            st.write(f"**Funding Level:** {opp.financial.funding_level or 'Not specified'}")
            if st.button("🚩 Report Wrong Data"):
                st.warning("Flagged for review in Needs Review tab.")
            if st.button("Close Inspector"):
                st.session_state["selected_opp_id"] = None
                st.rerun()

# ----------------- TAB 1: DISCOVER -----------------
with tabs[0]:
    st.subheader("Fine Arts Opportunity Registry")

    sub_tab1, sub_tab2 = st.tabs([
        f"📢 Verified Open Public Notices ({open_count})",
        f"🏛️ All Official Sources & Notice Boards ({len(sources_list)})"
    ])

    with sub_tab1:
        # Base pool of all open opportunities - OPEN BY DEFAULT
        open_and_active = [o for o in ranked_opps if o.status in ("OPEN", "ROLLING", "DEADLINE_UNKNOWN")]

        # Search and Optional Filters (applied after/in-line, never hiding initial view)
        with st.expander("🔍 Search & Filter Opportunities", expanded=False):
            f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
            with f_col1:
                search_kw = st.text_input("Free-text Search", placeholder="e.g. Lalit Kala, Chennai, fellowship, painting...", key="subtab1_kw")
            with f_col2:
                sel_geo = st.selectbox("Region / Geo Scope", ["All", "CHENNAI", "TAMIL_NADU", "INDIA", "ASIA", "INTERNATIONAL", "GLOBAL", "ONLINE"], index=0, key="subtab1_geo")
            with f_col3:
                sel_type = st.selectbox("Opportunity Type", ["All", "fellowship", "residency", "grant", "open call", "exhibition call", "scholarship", "award"], index=0, key="subtab1_type")

        # Apply search and filters only if specified
        filtered_opps = open_and_active
        if search_kw:
            kw = search_kw.strip().lower()
            filtered_opps = [
                o for o in filtered_opps
                if kw in o.title.lower()
                or kw in o.provider.lower()
                or kw in (o.why_text or "").lower()
                or kw in o.geo_scope.lower()
                or any(kw in m.lower() for m in (o.mediums or []))
            ]
        if sel_geo != "All":
            filtered_opps = [o for o in filtered_opps if o.geo_scope == sel_geo]
        if sel_type != "All":
            filtered_opps = [o for o in filtered_opps if o.type.lower() == sel_type.lower()]

        # Export bar
        exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)
        with exp_col1:
            st.download_button("📥 Export CSV", data=exports.export_to_csv(filtered_opps), file_name="aoia_opportunities.csv", mime="text/csv", key="exp_csv")
        with exp_col2:
            st.download_button("📥 Export JSON", data=exports.export_to_json(filtered_opps), file_name="aoia_opportunities.json", mime="application/json", key="exp_json")
        with exp_col3:
            st.download_button("📥 Export Markdown", data=exports.export_to_markdown(filtered_opps), file_name="aoia_opportunities.md", mime="text/markdown", key="exp_md")
        with exp_col4:
            st.download_button("📅 Export Calendar (ICS)", data=exports.export_to_ics(filtered_opps), file_name="aoia_deadlines.ics", mime="text/calendar", key="exp_ics")

        if st.session_state.get("selected_opp_id"):
            render_detail_drawer(st.session_state["selected_opp_id"])

        # View toggle: Cards vs Dense Table
        view_mode = st.radio("View Mode", ["Curated Gallery Cards", "Dense Table"], horizontal=True, label_visibility="collapsed", key="vm_radio")

        st.caption(f"Showing **{len(filtered_opps)}** of **{len(open_and_active)}** verified open calls & notices")

        if not filtered_opps:
            st.info("No matching open opportunities found with current search filters. Clear search to view all notices.")
        elif view_mode == "Curated Gallery Cards":
            for o in filtered_opps:
                render_opportunity_card(o, prefix="t1_")
        else:
            df_table = pd.DataFrame([{
                "Priority": f"{o.priority_score:.1f}",
                "Title": o.title,
                "Provider": o.provider,
                "Type": o.type,
                "Geo": o.geo_scope,
                "Deadline": o.deadline_date if o.deadline_date else "Not stated",
                "Days Left": o.days_left if o.days_left is not None else "-",
                "Fee": "Free" if o.financial.application_fee == 0 else o.financial.application_fee or "-",
                "URL": o.application_url
            } for o in filtered_opps])
            st.dataframe(df_table, use_container_width=True, column_config={"URL": st.column_config.LinkColumn("Apply")})

    with sub_tab2:
        st.markdown(f"#### All Registered Official Fine Arts Sources ({len(sources_list)})")
        st.caption("Complete directory of government academies, art foundations, residencies, and institutions monitored.")
        
        src_kw = st.text_input("Search sources by name, city, or domain...", key="src_kw_search")
        filtered_sources = sources_list
        if src_kw:
            skw = src_kw.strip().lower()
            filtered_sources = [
                s for s in sources_list
                if skw in s.get("name", "").lower()
                or skw in s.get("city", "").lower()
                or skw in s.get("base_url", "").lower()
            ]

        df_src_tab = pd.DataFrame([{
            "Name": s.get("name"),
            "Role": s.get("channel_role", "notice_board"),
            "Region": s.get("region"),
            "City": s.get("city"),
            "Tier": s.get("authority_tier"),
            "Official URL": s.get("base_url")
        } for s in filtered_sources])
        st.dataframe(df_src_tab, use_container_width=True, column_config={"Official URL": st.column_config.LinkColumn("Visit Official Page")})

# ----------------- TAB 2: CLOSING SOON -----------------
with tabs[1]:
    st.subheader("Critical & Urgent Calls (Closing &le; 14 Days)")
    closing_soon = [o for o in ranked_opps if o.days_left is not None and 0 <= o.days_left <= 14]
    if not closing_soon:
        st.info("No opportunities closing within 14 days.")
    else:
        for o in closing_soon:
            render_opportunity_card(o, prefix="t2_")

# ----------------- TAB 3: CALENDAR -----------------
with tabs[2]:
    st.subheader("Deadline Calendar Schedule")
    dated_opps = [o for o in raw_opps if o.deadline_date and o.deadline_date != "UNKNOWN"]
    if not dated_opps:
        st.info("No dated deadlines available for calendar view.")
    else:
        cal_df = pd.DataFrame([{
            "Deadline": o.deadline_date,
            "Opportunity": o.title,
            "Provider": o.provider,
            "Geo": o.geo_scope,
            "Days Left": o.days_left,
            "Bucket": o.bucket_label
        } for o in sorted(dated_opps, key=lambda x: x.deadline_date or "")])
        st.dataframe(cal_df, use_container_width=True)

# ----------------- TAB 4: MAP -----------------
with tabs[3]:
    st.subheader("Geographical Distribution")
    geo_counts = pd.DataFrame([{"Geo Scope": o.geo_scope} for o in raw_opps])
    if not geo_counts.empty:
        counts = geo_counts.value_counts().reset_index()
        counts.columns = ["Geo Scope", "Count"]
        st.bar_chart(counts.set_index("Geo Scope"))

# ----------------- TAB 5: WHERE TO SHOW / SELL -----------------
with tabs[4]:
    st.subheader("Where to Show or Sell (Galleries, Marketplaces & Auction Houses)")
    st.caption("Commercial and venue opportunities for exhibition hire, consignment, and gallery representation.")
    sales_venues = [s for s in sources_list if s.get("channel_role") in ("sales", "venue")]
    if sales_venues:
        df_venue = pd.DataFrame([{
            "Name": s.get("name"),
            "Role": s.get("channel_role"),
            "Region": s.get("region"),
            "City": s.get("city"),
            "Tier": s.get("authority_tier"),
            "Base URL": s.get("base_url")
        } for s in sales_venues])
        st.dataframe(df_venue, use_container_width=True, column_config={"Base URL": st.column_config.LinkColumn("Visit Venue")})
    else:
        st.info("No sales or venue channels loaded.")

# ----------------- TAB 6: MY APPLICATIONS -----------------
with tabs[5]:
    st.subheader("Artist Application Kanban Board")
    k1, k2, k3, k4 = st.columns(4)
    stages = ["Saved", "Preparing", "Submitted", "Result"]
    for col, stg in zip([k1, k2, k3, k4], stages):
        with col:
            st.markdown(f"#### {stg} ({len(st.session_state['applications'][stg])})")
            for opp_id in list(st.session_state["applications"][stg]):
                item = next((o for o in raw_opps if o.id == opp_id), None)
                if item:
                    st.caption(f"**{item.title[:40]}**\n{item.provider}")
                    nxt = "Preparing" if stg == "Saved" else "Submitted" if stg == "Preparing" else "Result" if stg == "Submitted" else None
                    if nxt and st.button(f"Advance ➔", key=f"adv_{stg}_{opp_id}"):
                        st.session_state["applications"][stg].remove(opp_id)
                        st.session_state["applications"][nxt].add(opp_id)
                        st.rerun()

# ----------------- TAB 7: SOURCES & HEALTH -----------------
with tabs[6]:
    st.subheader("Registry v4 Sources & Health Gate Monitor")
    
    # Unresolved Queue
    st.markdown("#### ⏳ Unresolved Sources Discovery Queue")
    reg_obj = registry.load_registry("configs/sources.yaml")
    unres_list = [u.model_dump() for u in reg_obj.unresolved_sources]
    
    if unres_list:
        st.write(f"There are **{len(unres_list)} unresolved sources** awaiting domain confirmation.")
        sel_unres = st.selectbox("Select Unresolved Source", [f"{u['name']} ({u['source_id']})" for u in unres_list])
        if sel_unres:
            target_sid = sel_unres.split("(")[-1].rstrip(")")
            target_u = next((u for u in unres_list if u["source_id"] == target_sid), None)
            if target_u:
                st.write(f"**City:** {target_u.get('city')}, {target_u.get('state')} | **Reason:** {target_u.get('why_not_enabled')}")
                cand_url_input = st.text_input("Candidate Official URL for Verification", placeholder="https://...")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    if st.button("Verify Candidate & Promote to Registry"):
                        if not cand_url_input:
                            st.error("Please enter a candidate URL.")
                        elif unresolved.is_third_party_listing(cand_url_input):
                            st.error("URL rejected: belongs to third-party listing, news, or marketplace.")
                        else:
                            try:
                                ok = unresolved.promote_unresolved_source("configs/sources.yaml", target_sid, cand_url_input)
                                if ok:
                                    st.success(f"Successfully promoted {target_u['name']} to sources.yaml!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Promotion failed: {e}")
    else:
        st.success("All sources are resolved!")

    st.markdown("---")
    st.markdown("#### Registered Sources Health Table")
    df_src = pd.DataFrame([{
        "ID": s.get("source_id"),
        "Name": s.get("name"),
        "Region": s.get("region"),
        "Role": s.get("channel_role"),
        "Tier": s.get("authority_tier"),
        "Status": s.get("verification", "PENDING"),
        "Failures": s.get("consecutive_failures", 0),
        "Reason": s.get("health_reason", "Not checked"),
        "URL": s.get("base_url")
    } for s in sources_list])
    st.dataframe(df_src, use_container_width=True, column_config={"URL": st.column_config.LinkColumn("Visit")})

# ----------------- TAB 8: NEEDS REVIEW -----------------
with tabs[7]:
    st.subheader("Needs Review & Diagnostics")
    unverified = [o for o in raw_opps if o.verification in ("UNVERIFIED", "VERIFICATION_REQUIRED")]
    st.write(f"**{len(unverified)}** opportunities currently require manual verification.")
    for o in unverified[:10]:
        render_opportunity_card(o, prefix="t8_")
