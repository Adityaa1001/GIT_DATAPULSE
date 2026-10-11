"""
DataPulse — Dashboard page.
Before/after comparison of a dataset: raw (as uploaded) vs. cleaned
(reflecting whatever fixes were accepted on the Quality Score page).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from modules import theme
from modules import mock_data
from modules import quality

theme.eyebrow_header("Stage 5 · Review", "Dashboard")

# ============================================================
# Dataset selector — same source as other pages
# ============================================================
fallback_files = ["customer_orders_q2.csv", "employee_master.xlsx", "vendor_ledger_2026.xlsx"]
available_files = (
    st.session_state["uploads_df"]["filename"].tolist()
    if "uploads_df" in st.session_state
    else fallback_files
)
selected_file = st.selectbox("Dataset", options=available_files, label_visibility="collapsed", key="dash_dataset_select")

# ============================================================
# Before = raw synthetic data. After = whatever's in Quality Score's
# working copy for this file, if the user has been there and accepted
# fixes — otherwise identical to "before" (nothing cleaned yet).
# ============================================================
before_df = mock_data.generate_dataset(selected_file)
qs_cleaned = st.session_state.get("qs_cleaned_data", {})
has_cleaning = selected_file in qs_cleaned
after_df = qs_cleaned[selected_file] if has_cleaning else before_df

before_score = quality.compute_quality_score(before_df)
after_score = quality.compute_quality_score(after_df)

if not has_cleaning:
    st.info(
        f"No cleaning has been applied to **{selected_file}** yet — this shows the raw dataset on both sides. "
        "Visit **Quality Score & AI Suggestions** and accept a few fixes, then come back here to see the comparison.",
        icon="ℹ️",
    )

# ============================================================
# KPI row — before vs after, with deltas
# ============================================================
k1, k2, k3, k4 = st.columns(4)
k1.metric("Quality Score", f"{after_score['overall']:.0f}", delta=f"{after_score['overall'] - before_score['overall']:+.0f}")

before_missing = before_df.isna().mean().mean() * 100
after_missing = after_df.isna().mean().mean() * 100
k2.metric("Avg Missing %", f"{after_missing:.1f}%", delta=f"{after_missing - before_missing:+.1f}%", delta_color="inverse")

before_dupes = int(before_df.duplicated().sum())
after_dupes = int(after_df.duplicated().sum())
k3.metric("Duplicate Rows", after_dupes, delta=after_dupes - before_dupes, delta_color="inverse")

before_rows = len(before_df)
after_rows = len(after_df)
k4.metric("Row Count", f"{after_rows:,}", delta=after_rows - before_rows, delta_color="off")

# ============================================================
# Radar chart — sub-score comparison (the flagship before/after visual)
# ============================================================
st.markdown("---")
r1, r2 = st.columns([1.3, 1])

with r1:
    with st.container(border=True):
        theme.eyebrow_header("Comparison", "Quality dimensions — before vs after")
        categories = ["Completeness", "Uniqueness", "Validity", "Consistency"]
        before_vals = [before_score["completeness"], before_score["uniqueness"], before_score["validity"], before_score["consistency"]]
        after_vals = [after_score["completeness"], after_score["uniqueness"], after_score["validity"], after_score["consistency"]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=before_vals + [before_vals[0]], theta=categories + [categories[0]],
            fill="toself", name="Before", line=dict(color=theme.DANGER, width=2),
            fillcolor="rgba(239,68,68,0.12)",
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=after_vals + [after_vals[0]], theta=categories + [categories[0]],
            fill="toself", name="After", line=dict(color=theme.SUCCESS, width=2),
            fillcolor="rgba(16,185,129,0.18)",
        ))
        fig_radar.update_layout(
            height=340,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=theme.BORDER, tickfont=dict(size=9, color=theme.TEXT_MUTED)),
                angularaxis=dict(gridcolor=theme.BORDER, tickfont=dict(size=11, color=theme.TEXT)),
            ),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1, font=dict(color=theme.TEXT_MUTED)),
            margin=dict(l=40, r=40, t=20, b=20),
        )
        st.plotly_chart(fig_radar, width="stretch", config={"displayModeBar": False})

with r2:
    with st.container(border=True):
        theme.eyebrow_header("Scores", "Overall composite")
        for label, before_v, after_v in [
            ("Before", before_score["overall"], None),
            ("After", after_score["overall"], None),
        ]:
            color = theme.DANGER if label == "Before" else theme.SUCCESS
            st.markdown(
                f"""
                <div style="display:flex; align-items:baseline; justify-content:space-between; padding:10px 0; border-bottom:1px solid {theme.BORDER};">
                    <span style="font-size:13px; color:{theme.TEXT_MUTED};">{label}</span>
                    <span style="font-family:'IBM Plex Mono',monospace; font-size:28px; font-weight:700; color:{color};">{before_v:.0f}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        improvement = after_score["overall"] - before_score["overall"]
        imp_color = theme.SUCCESS if improvement >= 0 else theme.DANGER
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:14px; padding:10px; background:rgba(16,185,129,0.06); border-radius:6px;">
                <span style="font-family:'IBM Plex Mono',monospace; font-size:15px; font-weight:600; color:{imp_color};">
                    {'▲' if improvement >= 0 else '▼'} {abs(improvement):.0f} pts
                </span>
                <div style="font-size:11px; color:{theme.TEXT_MUTED}; margin-top:2px;">net change</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# Missing values per column — grouped bar, before vs after
# ============================================================
st.markdown("---")
with st.container(border=True):
    theme.eyebrow_header("Detail", "Missing values by column — before vs after")

    columns = before_df.columns.tolist()
    before_missing_pct = [round(before_df[c].isna().mean() * 100, 1) for c in columns]
    after_missing_pct = [round(after_df[c].isna().mean() * 100, 1) if c in after_df.columns else 0 for c in columns]

    fig_bars = go.Figure()
    fig_bars.add_trace(go.Bar(name="Before", x=columns, y=before_missing_pct, marker_color=theme.DANGER))
    fig_bars.add_trace(go.Bar(name="After", x=columns, y=after_missing_pct, marker_color=theme.SUCCESS))
    fig_bars.update_layout(
        barmode="group", height=280,
        legend=dict(orientation="h", y=1.12, font=dict(color=theme.TEXT_MUTED)),
        margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Missing %",
    )
    st.plotly_chart(fig_bars, width="stretch", config={"displayModeBar": False})

# ============================================================
# Distribution overlay — shows outlier capping effect on 'amount'
# ============================================================
if "amount" in before_df.columns:
    with st.container(border=True):
        theme.eyebrow_header("Detail", "Value distribution — 'amount' before vs after")
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=before_df["amount"].dropna(), name="Before", marker_color=theme.DANGER,
            opacity=0.55, nbinsx=40,
        ))
        fig_dist.add_trace(go.Histogram(
            x=after_df["amount"].dropna() if "amount" in after_df.columns else [], name="After",
            marker_color=theme.SUCCESS, opacity=0.55, nbinsx=40,
        ))
        fig_dist.update_layout(
            barmode="overlay", height=260,
            legend=dict(orientation="h", y=1.12, font=dict(color=theme.TEXT_MUTED)),
            margin=dict(l=8, r=8, t=8, b=8),
        )
        st.plotly_chart(fig_dist, width="stretch", config={"displayModeBar": False})
        st.caption("Outlier capping (accepted on Quality Score) tightens the right tail of the distribution.")

st.caption(f"Comparing {selected_file} · {before_rows:,} → {after_rows:,} rows · scores computed live from current session state")