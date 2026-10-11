"""
DataPulse dark theme — high-density developer-tool design system.
Reference: Retool / Metabase / Datadog. Every screen imports this module
so the six application stages stay visually consistent.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

from modules import db

# ---------- Palette ----------
BG = "#0E1117"
SURFACE = "#161A23"
BORDER = "#262730"
TEXT = "#E5E7EB"
TEXT_MUTED = "#9CA3AF"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"
ACCENT = "#10B981"

STAGES = [
    "Login",
    "Upload",
    "Data Profiling",
    "Quality Score & AI Suggestions",
    "Dashboard",
    "Reports / Export",
]


def _flatten(html: str) -> str:
    """Strip leading whitespace per line so Streamlit's Markdown parser
    never mistakes indented HTML for a code block."""
    return "\n".join(line.strip() for line in html.strip().split("\n"))


CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {TEXT};
    font-size: 13.5px;
    line-height: 1.35;
}}

.stApp {{ background-color: {BG}; }}
[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
    pointer-events: none !important;
}}
[data-testid="stToolbar"] {{
    pointer-events: none !important;
}}
[data-testid="stHeader"] [data-testid="stSidebarCollapseButton"],
[data-testid="stHeader"] [data-testid="stExpandSidebarButton"] {{
    pointer-events: auto !important;
}}
[data-testid="stAppDeployButton"] {{ display: none !important; }}
[data-testid="stMainMenu"] {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}

/* ---------- Compact global spacing ---------- */
.block-container {{
    padding-top: 1.1rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}}
[data-testid="stVerticalBlock"] {{ gap: 0.55rem !important; }}
[data-testid="stHorizontalBlock"] {{ gap: 0.75rem !important; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 6px !important; }}
div[data-testid="stMarkdownContainer"] p {{ margin-bottom: 0.2rem; }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem !important; }}

.dp-brand {{
    display: flex; align-items: center; gap: 8px;
    padding: 4px 4px 16px 4px;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 14px;
}}
.dp-brand-name {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 14px;
    color: {TEXT};
    letter-spacing: -0.01em;
}}
.dp-brand-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {SUCCESS};
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
}}
.dp-sidebar-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: {TEXT_MUTED};
    padding: 0 4px;
    margin-top: 18px;
}}

/* Restyle the radio nav to look like a sidebar link list */
[data-testid="stSidebar"] [role="radiogroup"] {{ gap: 2px !important; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{
    padding: 6px 8px !important;
    border-radius: 5px !important;
    font-size: 13px !important;
}}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
    background-color: rgba(255,255,255,0.04) !important;
}}

/* ---------- KPI / metric cards ---------- */
[data-testid="stMetric"] {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 10px 14px 8px 14px;
}}
[data-testid="stMetricLabel"] {{
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: {TEXT_MUTED} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 22px !important;
    color: {TEXT} !important;
}}

/* ---------- Containers ---------- */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background-color: {SURFACE};
}}
div[data-testid="stExpander"], div[data-baseweb="card"] {{
    background-color: {SURFACE};
    border-color: {BORDER} !important;
}}

/* ---------- Status pills ---------- */
.dp-pill {{
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; font-weight: 500;
    padding: 2px 8px; border-radius: 3px;
    border: 1px solid transparent;
}}
.dp-pill-success {{ color: {SUCCESS}; background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); }}
.dp-pill-warning {{ color: {WARNING}; background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); }}
.dp-pill-danger  {{ color: {DANGER};  background: rgba(239,68,68,0.1);  border-color: rgba(239,68,68,0.3); }}
.dp-pill-dot {{ width: 5px; height: 5px; border-radius: 50%; }}
.dp-pill-success .dp-pill-dot {{ background: {SUCCESS}; }}
.dp-pill-warning .dp-pill-dot {{ background: {WARNING}; }}
.dp-pill-danger .dp-pill-dot  {{ background: {DANGER}; }}

/* ---------- Section labels ---------- */
.dp-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: {TEXT_MUTED}; margin-bottom: 2px;
}}
.dp-h {{ font-size: 15px; font-weight: 600; color: {TEXT}; margin: 4px 0 10px 0; }}

/* ---------- File uploader ---------- */
[data-testid="stFileUploaderDropzone"] {{
    background-color: {SURFACE} !important;
    border: 1px dashed {BORDER} !important;
    border-radius: 6px !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color: {ACCENT} !important; }}

/* ---------- Dataframe / data editor ---------- */
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
    border: 1px solid {BORDER} !important;
    border-radius: 6px !important;
}}

/* ---------- Buttons ---------- */
.stButton > button {{
    border-radius: 5px !important;
    font-size: 12.5px !important;
    padding: 4px 12px !important;
    border-color: {BORDER} !important;
}}
.stButton > button[kind="primary"] {{
    background-color: {ACCENT} !important;
    border-color: {ACCENT} !important;
    color: #0E1117 !important;
}}

/* ================= LOGIN BUTTON (in-flow, top-right of content) ================= */
.st-key-login_btn {{
    display: flex !important;
    justify-content: flex-end !important;
}}
.st-key-login_btn button {{
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    border: none !important;
    color: #0E1117 !important;
    background: linear-gradient(135deg, {SUCCESS}, #3B82F6) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    animation: dpPulseDot 2.6s infinite !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.st-key-login_btn button:hover {{
    transform: scale(1.08) !important;
    box-shadow: 0 6px 16px -4px rgba(16,185,129,0.55) !important;
}}
.st-key-login_btn button:active {{
    transform: scale(0.96) !important;
}}
.st-key-login_btn button p {{
    margin: 0 !important;
    font-size: 16px !important;
}}
@keyframes dpBtnPulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.45); }}
    70%  {{ box-shadow: 0 0 0 12px rgba(16,185,129,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
}}

/* ================= LOGIN SCREEN ================= */
.st-key-login_submit_btn {{
    display: flex !important;
    justify-content: center !important;
}}
.st-key-login_submit_btn button {{
    width: auto !important;
    padding: 13px 48px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    color: #0E1117 !important;
    background: linear-gradient(90deg, {SUCCESS}, #34D399, #3B82F6, {SUCCESS}) !important;
    background-size: 300% auto !important;
    animation: dpGradientShift 4s linear infinite, dpBtnPulse 2.4s ease-in-out infinite !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.st-key-login_submit_btn button:hover {{
    transform: translateY(-2px) scale(1.015) !important;
    box-shadow: 0 10px 24px -6px rgba(16,185,129,0.55) !important;
}}
.st-key-signup_btn {{
    width: 100% !important;
    display: block !important;
    margin-top: 14px !important;
    padding-top: 14px !important;
    border-top: 1px solid {BORDER} !important;
    text-align: center !important;
}}
.st-key-signup_btn button {{
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {TEXT_MUTED} !important;
    font-size: 13px !important;
    padding: 4px 0 !important;
}}
.st-key-signup_btn button:hover {{
    color: {ACCENT} !important;
    text-decoration: underline !important;
}}

.st-key-signup_submit_btn {{
    display: flex !important;
    justify-content: center !important;
}}
.st-key-signup_submit_btn button {{
    width: auto !important;
    padding: 13px 48px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    color: #0E1117 !important;
    background: linear-gradient(90deg, {SUCCESS}, #34D399, #3B82F6, {SUCCESS}) !important;
    background-size: 300% auto !important;
    animation: dpGradientShift 4s linear infinite, dpBtnPulse 2.4s ease-in-out infinite !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}}
.st-key-signup_submit_btn button:hover {{
    transform: translateY(-2px) scale(1.015) !important;
    box-shadow: 0 10px 24px -6px rgba(16,185,129,0.55) !important;
}}
.st-key-login_link_btn {{
    width: 100% !important;
    display: block !important;
    margin-top: 14px !important;
    padding-top: 14px !important;
    border-top: 1px solid {BORDER} !important;
    text-align: center !important;
}}
.st-key-login_link_btn button {{
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {TEXT_MUTED} !important;
    font-size: 13px !important;
    padding: 4px 0 !important;
}}
.st-key-login_link_btn button:hover {{
    color: {ACCENT} !important;
    text-decoration: underline !important;
}}

.dp-feature-item {{
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 14px;
}}
.dp-feature-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {SUCCESS};
    margin-top: 5px; flex-shrink: 0;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.15);
}}
.dp-feature-title {{ font-size: 13.5px; font-weight: 600; color: {TEXT}; }}
.dp-feature-desc {{ font-size: 12px; color: {TEXT_MUTED}; margin-top: 1px; }}

.dp-divider {{
    display: flex; align-items: center; gap: 10px;
    margin: 16px 0;
    color: {TEXT_MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;
}}
.dp-divider::before, .dp-divider::after {{
    content: ""; flex: 1; height: 1px; background: {BORDER};
}}

.dp-login-hero-title {{ font-size: 30px; margin: 10px 0 8px 0; }}
.dp-login-hero-tagline {{ color: {TEXT_MUTED}; font-size: 13.5px; margin-bottom: 28px; max-width: 380px; }}

/* ================= PAGE FOOTER NAV (prev/next) ================= */
.dp-footer-nav-caption {{
    text-align: center; font-size: 11.5px; color: {TEXT_MUTED};
    font-family: 'IBM Plex Mono', monospace;
    margin: 4px 0 10px 0;
}}
.st-key-nav_prev_btn button {{
    border-color: {BORDER} !important;
    color: {TEXT_MUTED} !important;
}}
.st-key-nav_prev_btn button:hover {{
    border-color: {ACCENT} !important;
    color: {TEXT} !important;
}}
.st-key-nav_next_btn button {{
    background-color: {ACCENT} !important;
    border-color: {ACCENT} !important;
    color: #0E1117 !important;
    font-weight: 600 !important;
}}

/* ================= ANIMATED SIGNAL LOGO (continuous loop) ================= */
.dp-signal-scroll {{
    width: 32px; height: 18px;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
}}
.dp-signal-scroll svg {{
    display: block;
    animation: dpSignalScroll 1.4s linear infinite;
}}
@keyframes dpSignalScroll {{
    from {{ transform: translateX(0); }}
    to   {{ transform: translateX(-32px); }}
}}

/* ================= ANIMATED GRADIENT BRAND NAME ================= */
.dp-brand-name-glow {{
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    letter-spacing: -0.01em;
    background: linear-gradient(90deg, {SUCCESS}, #34D399, #3B82F6, {SUCCESS});
    background-size: 300% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: dpGradientShift 4s linear infinite;
}}
@keyframes dpGradientShift {{
    to {{ background-position: 300% center; }}
}}

/* ================= MARKETING BANNER ================= */
.dp-banner {{
    position: relative;
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 22px 26px 20px 26px;
    margin-bottom: 18px;
    overflow: hidden;
}}
.dp-banner-glow {{
    position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(16,185,129,0.14), transparent 70%);
    pointer-events: none;
}}
.dp-banner-top {{ display: flex; align-items: center; gap: 10px; position: relative; z-index: 1; }}
.dp-banner-title {{ font-size: 22px; }}
.dp-banner-tagline {{
    color: {TEXT_MUTED}; font-size: 13px; margin-top: 6px;
    position: relative; z-index: 1; max-width: 640px;
}}
.dp-banner-stats {{ display: flex; gap: 32px; margin-top: 18px; position: relative; z-index: 1; }}
.dp-banner-stat-value {{
    font-family: 'IBM Plex Mono', monospace; font-size: 19px; font-weight: 600; color: {TEXT};
}}
.dp-banner-stat-label {{
    font-size: 10.5px; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em;
}}

/* ================= SIDEBAR — richer sections ================= */
.dp-sb-section {{
    margin-top: 16px; padding-top: 12px;
    border-top: 1px solid {BORDER};
}}
.dp-sb-label {{
    font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.06em;
    color: {TEXT_MUTED}; margin-bottom: 8px; font-family: 'IBM Plex Mono', monospace;
}}
.dp-step {{
    display: flex; align-items: center; gap: 8px;
    padding: 4px 2px; font-size: 12.5px;
}}
.dp-step-dot {{ width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }}
.dp-step-done .dp-step-dot {{ background: {SUCCESS}; }}
.dp-step-active .dp-step-dot {{
    background: {SUCCESS};
    box-shadow: 0 0 0 3px rgba(16,185,129,0.22);
    animation: dpPulseDot 1.8s infinite;
}}
.dp-step-pending .dp-step-dot {{ background: {BORDER}; border: 1px solid #3A3D46; }}
.dp-step-done span.dp-step-label {{ color: {TEXT_MUTED}; text-decoration: line-through; text-decoration-color: {BORDER}; }}
.dp-step-active span.dp-step-label {{ color: {TEXT}; font-weight: 600; }}
.dp-step-pending span.dp-step-label {{ color: {TEXT_MUTED}; }}
@keyframes dpPulseDot {{
    0%   {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }}
    70%  {{ box-shadow: 0 0 0 6px rgba(16,185,129,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
}}

.dp-status-card {{
    background: rgba(255,255,255,0.02);
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 12px;
}}
.dp-status-row {{ display: flex; justify-content: space-between; padding: 2px 0; color: {TEXT_MUTED}; }}
.dp-status-row span.val {{ color: {TEXT}; font-family: 'IBM Plex Mono', monospace; }}

.dp-quickstat {{ display: flex; justify-content: space-between; padding: 3px 0; font-size: 12.5px; }}
.dp-quickstat .label {{ color: {TEXT_MUTED}; }}
.dp-quickstat .value {{ font-family: 'IBM Plex Mono', monospace; color: {TEXT}; font-weight: 500; }}

.dp-profile-footer {{
    display: flex; align-items: center; gap: 8px;
    padding-top: 4px;
}}
.dp-avatar {{
    width: 26px; height: 26px; border-radius: 50%;
    background: linear-gradient(135deg, {SUCCESS}, #3B82F6);
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; color: #0E1117;
    flex-shrink: 0;
}}
.dp-profile-name {{ font-size: 12px; color: {TEXT}; font-weight: 500; }}
.dp-profile-role {{ font-size: 10.5px; color: {TEXT_MUTED}; }}
</style>
"""


SIGNAL_SVG_LOOP = """
<div class="dp-signal-scroll">
<svg width="64" height="18" viewBox="0 0 64 18" xmlns="http://www.w3.org/2000/svg">
<polyline points="0,9 5,9 7,3 9,15 11,9 32,9 37,9 39,3 41,15 43,9 64,9"
fill="none" stroke="#10B981" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
</svg>
</div>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def sidebar_nav(active_stage: str) -> str:
    """Renders the sidebar: animated brand mark, nav list, pipeline stepper,
    system status card, quick stats, and a profile footer.
    Returns the currently selected stage name."""
    with st.sidebar:
        # --- Animated brand ---
        st.markdown(
            _flatten(f"""
                {SIGNAL_SVG_LOOP}
                """),
            unsafe_allow_html=True,
        )
        st.markdown(
            _flatten(f"""
                <div class="dp-brand" style="border-bottom:none; margin-bottom:6px; padding-bottom:0;">
                    <span class="dp-brand-name-glow dp-banner-title" style="font-size:17px;">DataPulse</span>
                </div>
                """),
            unsafe_allow_html=True,
        )

        # --- Nav list ---
        selected = st.radio(
            "Navigation",
            STAGES,
            index=STAGES.index(active_stage) if active_stage in STAGES else 0,
            label_visibility="collapsed",
        )

        # --- Pipeline stepper ---
        st.markdown('<div class="dp-sb-section">', unsafe_allow_html=True)
        st.markdown('<div class="dp-sb-label">Pipeline progress</div>', unsafe_allow_html=True)
        active_idx = STAGES.index(active_stage) if active_stage in STAGES else 0
        steps_html = ""
        for i, stage in enumerate(STAGES):
            state = "done" if i < active_idx else ("active" if i == active_idx else "pending")
            steps_html += f'<div class="dp-step dp-step-{state}"><span class="dp-step-dot"></span><span class="dp-step-label">{stage}</span></div>'
        st.markdown(_flatten(steps_html), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- System status ---
        db_ok = db.is_available()
        db_label = "Connected" if db_ok else "Offline (session only)"
        db_color = SUCCESS if db_ok else DANGER
        st.markdown('<div class="dp-sb-section">', unsafe_allow_html=True)
        st.markdown('<div class="dp-sb-label">System status</div>', unsafe_allow_html=True)
        st.markdown(
            _flatten(f"""
                <div class="dp-status-card">
                    <div class="dp-status-row">Status <span class="val" style="color:{SUCCESS};">● Operational</span></div>
                    <div class="dp-status-row">Database <span class="val" style="color:{db_color};">● {db_label}</span></div>
                    <div class="dp-status-row">Environment <span class="val">local</span></div>
                    <div class="dp-status-row">Version <span class="val">v0.2.0</span></div>
                </div>
                """),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Quick stats ---
        st.markdown('<div class="dp-sb-section">', unsafe_allow_html=True)
        st.markdown('<div class="dp-sb-label">Quick stats</div>', unsafe_allow_html=True)
        st.markdown(
            _flatten("""
                <div class="dp-quickstat"><span class="label">Datasets processed</span><span class="value">1,248</span></div>
                <div class="dp-quickstat"><span class="label">Avg quality score</span><span class="value">78</span></div>
                <div class="dp-quickstat"><span class="label">Storage used</span><span class="value">4.2 GB</span></div>
                """),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Profile footer ---
        current_user = st.session_state.get("dp_user")
        if current_user:
            profile_email = current_user["email"]
            profile_role = "Signed in"
            avatar_letter = profile_email[0].upper()
        else:
            profile_email = "Not signed in"
            profile_role = "Guest · DataPulse"
            avatar_letter = "?"
        st.markdown('<div class="dp-sb-section">', unsafe_allow_html=True)
        st.markdown(
            _flatten(f"""
                <div class="dp-profile-footer">
                    <div class="dp-avatar">{avatar_letter}</div>
                    <div>
                        <div class="dp-profile-name">{profile_email}</div>
                        <div class="dp-profile-role">{profile_role}</div>
                    </div>
                </div>
                """),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return selected


def login_button():
    """Small circular avatar/profile icon button, top-right of the page.
    On click, opens a floating modal dialog with email/password + a
    create-account action — call this from the top-right column of any page."""
    current_user = st.session_state.get("dp_user")
    label = current_user["email"][0].upper() if current_user else "T"
    if st.button(label, key="login_btn", type="primary"):
        open_login_dialog()
    render_active_dialog()


def open_login_dialog():
    """Sets the active dialog flag to 'login'. Call this from top-level
    script code (e.g. when the sidebar's 'Login' nav item is selected),
    then call render_active_dialog() afterward to actually show it."""
    st.session_state["dp_active_dialog"] = "login"


def render_active_dialog():
    """Renders whichever dialog is currently 'active', based on session
    state. Must be called from top-level script code, never from inside
    another dialog — Streamlit forbids nesting dialogs. Switching between
    the login/signup dialogs works by setting the flag then calling
    st.rerun(), so the next dialog opens fresh from here instead of being
    called directly from within the one that's closing."""
    active = st.session_state.get("dp_active_dialog")
    if active == "login":
        _open_login_dialog()
    elif active == "signup":
        _open_signup_dialog()


@st.dialog("Sign in to DataPulse")
def _open_login_dialog():
    st.markdown(
        _flatten(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">
                {SIGNAL_SVG_LOOP}
                <span class="dp-brand-name-glow" style="font-size:16px;">DataPulse</span>
            </div>
            """),
        unsafe_allow_html=True,
    )

    email = st.text_input("Email", placeholder="you@srm.edu.in", key="dialog_email")
    password = st.text_input("Password", type="password", placeholder="••••••••", key="dialog_password")

    if st.button("Sign In", type="primary", key="login_submit_btn"):
        if not email or not password:
            st.error("Enter both email and password.")
        elif not db.is_available():
            st.error("Database unavailable — can't sign in right now. Check that MySQL is running.")
        else:
            user = db.verify_user(email, password)
            if user:
                st.session_state["dp_user"] = user
                st.session_state["dp_active_dialog"] = None
                st.toast(f"Welcome back, {user['email']}!", icon="✅")
                st.rerun()
            else:
                st.error("Incorrect email or password.")

    if st.button("Create new account", key="signup_btn"):
        st.session_state["dp_active_dialog"] = "signup"
        st.rerun()


@st.dialog("Create your account")
def _open_signup_dialog():
    st.markdown(
        _flatten(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px;">
                {SIGNAL_SVG_LOOP}
                <span class="dp-brand-name-glow" style="font-size:16px;">DataPulse</span>
            </div>
            """),
        unsafe_allow_html=True,
    )

    email = st.text_input("Email", placeholder="you@srm.edu.in", key="signup_email")
    new_password = st.text_input("New password", type="password", placeholder="••••••••", key="signup_new_password")
    confirm_password = st.text_input("Re-enter password", type="password", placeholder="••••••••", key="signup_confirm_password")

    if st.button("Create account", type="primary", key="signup_submit_btn"):
        if not email or not new_password or not confirm_password:
            st.error("Fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif len(new_password) < 6:
            st.error("Password should be at least 6 characters.")
        elif not db.is_available():
            st.error("Database unavailable — can't create an account right now. Check that MySQL is running.")
        else:
            ok, msg = db.create_user(email, new_password)
            if ok:
                st.toast("Account created successfully!", icon="✅")
                st.session_state["dp_active_dialog"] = "login"
                st.rerun()
            else:
                st.error(msg)

    if st.button("Already have an account? Sign in", key="login_link_btn"):
        st.session_state["dp_active_dialog"] = "login"
        st.rerun()


def feature_item(title: str, desc: str):
    st.markdown(
        _flatten(f"""
            <div class="dp-feature-item">
                <div class="dp-feature-dot"></div>
                <div>
                    <div class="dp-feature-title">{title}</div>
                    <div class="dp-feature-desc">{desc}</div>
                </div>
            </div>
            """),
        unsafe_allow_html=True,
    )


def divider(label: str = "or"):
    st.markdown(f'<div class="dp-divider">{label}</div>', unsafe_allow_html=True)


def banner():
    """Marketing/hero banner for the top of the app — animated logo,
    gradient brand name, tagline, and headline stats."""
    st.markdown(
        _flatten(f"""
            <div class="dp-banner">
                <div class="dp-banner-glow"></div>
                <div class="dp-banner-top">
                    {SIGNAL_SVG_LOOP}
                    <span class="dp-brand-name-glow dp-banner-title">DataPulse</span>
                </div>
                <div class="dp-banner-tagline">
                    Automated data cleaning &amp; quality scoring for modern data teams —
                    upload, profile, clean, and export with a full audit trail in minutes, not hours.
                </div>
                <div class="dp-banner-stats">
                    <div><div class="dp-banner-stat-value">1,248</div><div class="dp-banner-stat-label">Datasets cleaned</div></div>
                    <div><div class="dp-banner-stat-value">+34%</div><div class="dp-banner-stat-label">Avg quality uplift</div></div>
                    <div><div class="dp-banner-stat-value">6</div><div class="dp-banner-stat-label">Active pipelines</div></div>
                    <div><div class="dp-banner-stat-value" style="color:{SUCCESS};">● Live</div><div class="dp-banner-stat-label">System status</div></div>
                </div>
            </div>
            """),
        unsafe_allow_html=True,
    )


def pill(text: str, kind: str = "success") -> str:
    return _flatten(f"""
        <span class="dp-pill dp-pill-{kind}"><span class="dp-pill-dot"></span>{text}</span>
        """)


def eyebrow_header(eyebrow: str, title: str):
    st.markdown(
        _flatten(f"""
            <div class="dp-eyebrow">{eyebrow}</div>
            <div class="dp-h">{title}</div>
            """),
        unsafe_allow_html=True,
    )


# The real navigable pages, in pipeline order (excludes "Login", which
# opens a modal rather than being a page).
PAGE_STAGES = [s for s in STAGES if s != "Login"]


def page_nav_footer(current_title: str, page_map: dict):
    """Renders a Previous/Next footer bar at the bottom of a page, driven
    by PAGE_STAGES order. `page_map` maps stage title -> st.Page object,
    same dict app.py already builds for the sidebar switch logic."""
    if current_title not in PAGE_STAGES:
        return
    idx = PAGE_STAGES.index(current_title)
    step_num = idx + 1
    total = len(PAGE_STAGES)

    st.markdown("---")
    st.markdown(f'<div class="dp-footer-nav-caption">STEP {step_num} OF {total}</div>', unsafe_allow_html=True)

    col_prev, col_spacer, col_next = st.columns([2, 3, 2])
    with col_prev:
        if idx > 0:
            prev_title = PAGE_STAGES[idx - 1]
            if st.button(f"← {prev_title}", key="nav_prev_btn", width="stretch"):
                st.switch_page(page_map[prev_title])
    with col_next:
        if idx < total - 1:
            next_title = PAGE_STAGES[idx + 1]
            if st.button(f"{next_title} →", key="nav_next_btn", width="stretch", type="primary"):
                st.switch_page(page_map[next_title])


def apply_plotly_dark_template():
    """Registers a Plotly template matching the app's dark surface exactly
    (transparent backgrounds, muted gridlines, mono-ish axis text)."""
    template = go.layout.Template()
    template.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans, sans-serif", color=TEXT_MUTED, size=11),
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUTED)),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, linecolor=BORDER, tickfont=dict(color=TEXT_MUTED)),
        margin=dict(l=8, r=8, t=8, b=8),
        legend=dict(font=dict(color=TEXT_MUTED)),
        colorway=[SUCCESS, WARNING, DANGER, "#3B82F6", "#8B5CF6"],
    )
    pio.templates["datapulse_dark"] = template
    pio.templates.default = "datapulse_dark"