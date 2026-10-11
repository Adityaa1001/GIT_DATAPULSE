"""
DataPulse — entry point.

This is the only file you run: `streamlit run app.py`.
It sets up the page config, theme, and custom sidebar ONCE, wires our
existing animated sidebar nav to Streamlit's real multi-page routing
(st.navigation + st.switch_page), and renders whichever page is active.
Session state (e.g. uploaded files) is now genuinely shared across every
page, since it's all one running app instead of separate scripts.
"""

import streamlit as st

from modules import theme
from modules import db

st.set_page_config(
    page_title="DataPulse",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject()
theme.apply_plotly_dark_template()
db.init_db()  # no-op / safe to fail if MySQL isn't running yet

# ============================================================
# Define pages
# ============================================================
upload_page = st.Page("pages/upload.py", title="Upload", default=True)
profiling_page = st.Page("pages/data_profiling.py", title="Data Profiling")
quality_page = st.Page("pages/quality_score.py", title="Quality Score & AI Suggestions")
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard")
reports_page = st.Page("pages/reports.py", title="Reports / Export")

# Streamlit's own nav UI is hidden — we keep using our custom animated
# sidebar, and drive real page switches from it below.
current_page = st.navigation(
    [upload_page, profiling_page, quality_page, dashboard_page, reports_page],
    position="hidden",
)

# ============================================================
# Custom sidebar (brand, pipeline stepper, status, quick stats)
# ============================================================
page_titles_to_pages = {
    "Upload": upload_page,
    "Data Profiling": profiling_page,
    "Quality Score & AI Suggestions": quality_page,
    "Dashboard": dashboard_page,
    "Reports / Export": reports_page,
}

selected_stage = theme.sidebar_nav(active_stage=current_page.title)

if selected_stage == "Login":
    # Login isn't a page — it opens the floating modal instead of navigating.
    theme.open_login_dialog()
elif selected_stage != current_page.title:
    st.switch_page(page_titles_to_pages[selected_stage])

# ============================================================
# Top-right profile/login icon (shows on every page, shared dialog state)
# ============================================================
top_spacer, top_login = st.columns([6, 1])
with top_login:
    theme.login_button()

# ============================================================
# Render the active page's content
# ============================================================
current_page.run()

# ============================================================
# Previous / Next footer navigation
# ============================================================
theme.page_nav_footer(current_page.title, page_titles_to_pages)