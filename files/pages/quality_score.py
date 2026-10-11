"""
DataPulse — Quality Score & AI Suggestions page.
Rule-based detection (missing values, duplicates, outliers) packaged as
human-readable suggestions with an accept/reject workflow. Not a trained
ML model — see the description text on-page for why that's the design.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from modules import theme
from modules import mock_data
from modules import quality
from modules import db

theme.eyebrow_header("Stage 4 · Scoring", "Quality Score & AI Suggestions")

# ============================================================
# Dataset selector — same source as Data Profiling
# ============================================================
fallback_files = ["customer_orders_q2.csv", "employee_master.xlsx", "vendor_ledger_2026.xlsx"]
available_files = (
    st.session_state["uploads_df"]["filename"].tolist()
    if "uploads_df" in st.session_state
    else fallback_files
)
selected_file = st.selectbox("Dataset", options=available_files, label_visibility="collapsed", key="qs_dataset_select")

generate_suggestions = quality.generate_suggestions
apply_suggestion = quality.apply_suggestion
compute_quality_score = quality.compute_quality_score


# ============================================================
# Session state — working copy of the data + suggestion statuses,
# keyed per filename so switching datasets doesn't mix state up
# ============================================================
st.session_state.setdefault("qs_cleaned_data", {})
st.session_state.setdefault("qs_suggestions", {})

if selected_file not in st.session_state.qs_cleaned_data:
    raw_df = mock_data.generate_dataset(selected_file)
    st.session_state.qs_cleaned_data[selected_file] = raw_df
    st.session_state.qs_suggestions[selected_file] = generate_suggestions(raw_df)

current_df = st.session_state.qs_cleaned_data[selected_file]
suggestions = st.session_state.qs_suggestions[selected_file]
score = compute_quality_score(current_df)

reset_col, _ = st.columns([1, 5])
with reset_col:
    if st.button("Reset dataset", key="qs_reset"):
        raw_df = mock_data.generate_dataset(selected_file)
        st.session_state.qs_cleaned_data[selected_file] = raw_df
        st.session_state.qs_suggestions[selected_file] = generate_suggestions(raw_df)
        st.rerun()

# ============================================================
# Composite score + sub-scores
# ============================================================
score_col, bars_col = st.columns([1, 2])

with score_col:
    with st.container(border=True):
        st.markdown('<div class="dp-eyebrow">Composite</div>', unsafe_allow_html=True)
        score_color = theme.SUCCESS if score["overall"] >= 75 else theme.WARNING if score["overall"] >= 50 else theme.DANGER
        st.markdown(
            f'<div style="font-family:\'IBM Plex Mono\',monospace; font-size:52px; font-weight:700; color:{score_color};">{score["overall"]:.0f}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Data Quality Score")

with bars_col:
    with st.container(border=True):
        theme.eyebrow_header("Sub-scores", "Breakdown")
        for label, key in [("Completeness", "completeness"), ("Uniqueness", "uniqueness"),
                            ("Validity", "validity"), ("Consistency", "consistency")]:
            val = score[key]
            bar_color = theme.SUCCESS if val >= 75 else theme.WARNING if val >= 50 else theme.DANGER
            st.markdown(
                theme._flatten(f"""
                    <div style="margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; font-size:12.5px; margin-bottom:3px;">
                            <span style="color:{theme.TEXT_MUTED};">{label}</span>
                            <span style="font-family:'IBM Plex Mono',monospace; color:{theme.TEXT};">{val:.0f}%</span>
                        </div>
                        <div style="background:{theme.BORDER}; border-radius:4px; height:6px; overflow:hidden;">
                            <div style="background:{bar_color}; width:{val}%; height:100%;"></div>
                        </div>
                    </div>
                    """),
                unsafe_allow_html=True,
            )

# ============================================================
# Suggestion counts
# ============================================================
pending = [s for s in suggestions if s["status"] == "pending"]
accepted = [s for s in suggestions if s["status"] == "accepted"]
rejected = [s for s in suggestions if s["status"] == "rejected"]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total suggestions", len(suggestions))
k2.metric("Pending", len(pending))
k3.metric("Accepted", len(accepted))
k4.metric("Rejected", len(rejected))

# ============================================================
# AI Suggestions list
# ============================================================
st.markdown("---")
theme.eyebrow_header("AI Suggestions", "Review and apply cleaning recommendations")
st.caption(
    "Detected using rule-based statistics (missing-value counts, duplicate detection, "
    "Z-score outlier analysis) — not a trained model. You decide what gets applied."
)

if not suggestions:
    st.success("No issues detected in this dataset.")
else:
    for s in suggestions:
        with st.container(border=True):
            col_main, col_action = st.columns([4, 1])
            with col_main:
                icon = {"missing": "🟡", "duplicate": "🔴", "outlier": "🟠"}.get(s["issue_type"], "⚪")
                st.markdown(f"**{icon} {s['description']}**")
                st.caption(f"Suggested fix: {s['fix_description']}")
            with col_action:
                if s["status"] == "pending":
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Accept", key=f"accept_{s['id']}", type="primary"):
                            st.session_state.qs_cleaned_data[selected_file] = apply_suggestion(current_df, s)
                            s["status"] = "accepted"
                            st.session_state.setdefault("audit_log", []).append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "filename": selected_file,
                                "action": "accepted",
                                "column": s["column"],
                                "issue_type": s["issue_type"],
                                "description": s["description"],
                                "fix_applied": s["fix_description"],
                            })
                            db.insert_audit_log(
                                filename=selected_file, action="accepted", column_name=s["column"],
                                issue_type=s["issue_type"], description=s["description"],
                                fix_applied=s["fix_description"],
                            )
                            st.rerun()
                    with b2:
                        if st.button("Reject", key=f"reject_{s['id']}"):
                            s["status"] = "rejected"
                            st.session_state.setdefault("audit_log", []).append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "filename": selected_file,
                                "action": "rejected",
                                "column": s["column"],
                                "issue_type": s["issue_type"],
                                "description": s["description"],
                                "fix_applied": "(none — rejected)",
                            })
                            db.insert_audit_log(
                                filename=selected_file, action="rejected", column_name=s["column"],
                                issue_type=s["issue_type"], description=s["description"],
                                fix_applied="(none - rejected)",
                            )
                            st.rerun()
                elif s["status"] == "accepted":
                    st.markdown(theme.pill("Accepted", "success"), unsafe_allow_html=True)
                else:
                    st.markdown(theme.pill("Rejected", "danger"), unsafe_allow_html=True)

st.caption(f"Working on {selected_file} · {len(current_df):,} rows × {len(current_df.columns)} columns · scores recompute live as you accept fixes")