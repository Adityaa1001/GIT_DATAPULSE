"""
DataPulse — Login / Signup screen.
Same dark developer-tool design system as the rest of the app.
"""

import streamlit as st

from modules import theme

st.set_page_config(
    page_title="DataPulse — Login",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject()
theme.sidebar_nav(active_stage="Login")

st.write("")
left, right = st.columns([1.1, 1], gap="large")

# ============================================================
# Left — hero + feature highlights
# ============================================================
with left:
    st.markdown(
        theme._flatten(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-top:24px;">
                {theme.SIGNAL_SVG_LOOP}
                <span class="dp-brand-name-glow dp-login-hero-title">DataPulse</span>
            </div>
            """),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="dp-login-hero-tagline">'
        'Automated data cleaning &amp; quality scoring for modern data teams. '
        'Sign in to pick up where your team left off.'
        '</div>',
        unsafe_allow_html=True,
    )

    theme.feature_item(
        "Automated profiling",
        "Instant missing-value, duplicate, and outlier detection on upload.",
    )
    theme.feature_item(
        "AI-assisted cleaning",
        "Accept or reject suggested fixes — human-in-the-loop, never fully automatic.",
    )
    theme.feature_item(
        "Composite quality score",
        "Completeness, uniqueness, validity, and consistency in one number.",
    )
    theme.feature_item(
        "Full audit trail",
        "Every change is logged and exportable alongside your cleaned dataset.",
    )

    st.write("")
    st.markdown(
        theme._flatten(f"""
            <div class="dp-status-card" style="max-width:380px;">
                <div class="dp-status-row">Status <span class="val" style="color:{theme.SUCCESS};">● Operational</span></div>
                <div class="dp-status-row">Datasets cleaned <span class="val">1,248</span></div>
                <div class="dp-status-row">Active pipelines <span class="val">6</span></div>
            </div>
            """),
        unsafe_allow_html=True,
    )

# ============================================================
# Right — sign-in card
# ============================================================
with right:
    with st.container(border=True):
        st.markdown('<div class="dp-eyebrow">Welcome back</div>', unsafe_allow_html=True)
        st.markdown('<div class="dp-h" style="font-size:19px;">Sign in to DataPulse</div>', unsafe_allow_html=True)

        with st.form("login_form", border=False):
            email = st.text_input("Email", placeholder="you@srm.edu.in")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            c1, c2 = st.columns([1, 1])
            with c1:
                st.checkbox("Remember me")
            with c2:
                st.markdown(
                    '<div style="text-align:right; padding-top:8px;">'
                    f'<span style="font-size:12px; color:{theme.TEXT_MUTED};">Forgot password?</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            submitted = st.form_submit_button("Sign In", type="primary", key="login_submit_btn")
            if submitted:
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    st.success(f"Welcome back — signed in as {email} (demo only, not wired to auth yet).")

        theme.divider("or")

        st.button("Create an account", key="signup_btn")

        st.caption("Auth module owner: whoever's building Auth & Core Backend — this screen is UI-only for now.")