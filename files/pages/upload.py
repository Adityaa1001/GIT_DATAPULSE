"""
DataPulse — Upload page (multi-page: setup/nav/theme handled by app.py entry).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

from modules import theme
from modules import db

theme.banner()

# ============================================================
# Mock data generation (realistic, deterministic per session)
# ============================================================
if "uploads_df" not in st.session_state:
    rng = np.random.default_rng(seed=7)
    n = 18
    filenames = [
        "customer_orders_q2.csv", "employee_master.xlsx", "inventory_raw.csv",
        "vendor_ledger_2026.xlsx", "web_events_export.csv", "support_tickets_jul.csv",
        "product_catalog_v3.xlsx", "payroll_master.csv", "shipment_logs.csv",
        "crm_leads_export.xlsx", "warehouse_stock.csv", "ad_spend_report.xlsx",
        "returns_processed.csv", "survey_responses_q2.csv", "clickstream_sample.csv",
        "finance_gl_export.xlsx", "hr_attrition_data.csv", "sales_pipeline_snapshot.xlsx",
    ]
    statuses = rng.choice(
        ["cleaned", "needs_review", "error"], size=n, p=[0.5, 0.35, 0.15]
    )
    dq_scores = np.where(
        statuses == "cleaned", rng.integers(80, 99, n),
        np.where(statuses == "needs_review", rng.integers(45, 79, n), 0),
    )
    base_date = datetime.now()
    df = pd.DataFrame({
        "filename": filenames[:n],
        "uploaded_at": [base_date - timedelta(days=int(d), hours=int(h))
                         for d, h in zip(rng.integers(0, 21, n), rng.integers(0, 23, n))],
        "rows": rng.integers(400, 42000, n),
        "columns": rng.integers(6, 34, n),
        "missing_pct": np.round(rng.uniform(0, 22, n), 1),
        "duplicate_pct": np.round(rng.uniform(0, 9, n), 1),
        "status": statuses,
        "dq_score": dq_scores,
        "reviewed": statuses == "cleaned",
    }).sort_values("uploaded_at", ascending=False).reset_index(drop=True)
    st.session_state.uploads_df = df

# ============================================================
# Header + file intake
# ============================================================
theme.eyebrow_header("Stage 2 · Intake", "Upload dataset")

top_l, top_r = st.columns([3, 1])
with top_l:
    uploaded_file = st.file_uploader(
        "Upload", type=["csv", "xlsx"], label_visibility="collapsed"
    )
with top_r:
    st.caption("Accepted: .csv, .xlsx · Max 200MB per file")

if uploaded_file is not None:
    try:
        new_df = (
            pd.read_csv(uploaded_file)
            if uploaded_file.name.endswith(".csv")
            else pd.read_excel(uploaded_file)
        )
        st.session_state.uploads_df = pd.concat(
            [
                pd.DataFrame([{
                    "filename": uploaded_file.name,
                    "uploaded_at": datetime.now(),
                    "rows": len(new_df),
                    "columns": len(new_df.columns),
                    "missing_pct": round(new_df.isna().mean().mean() * 100, 1),
                    "duplicate_pct": round(new_df.duplicated().mean() * 100, 1),
                    "status": "needs_review",
                    "dq_score": 0,
                    "reviewed": False,
                }]),
                st.session_state.uploads_df,
            ],
            ignore_index=True,
        )
        st.success(f"{uploaded_file.name} — {len(new_df):,} rows × {len(new_df.columns)} cols ingested.")

        # Best-effort persistence to MySQL — the app keeps working on
        # session state alone if the DB isn't reachable.
        current_user = st.session_state.get("dp_user")
        upload_id = db.insert_upload(
            filename=uploaded_file.name,
            user_id=current_user["id"] if current_user else None,
            row_count=len(new_df),
            column_count=len(new_df.columns),
            missing_pct=round(new_df.isna().mean().mean() * 100, 1),
            duplicate_pct=round(new_df.duplicated().mean() * 100, 1),
            status="needs_review",
            dq_score=0,
        )
        if upload_id:
            st.caption(f"Saved to database (upload #{upload_id}).")
        elif not db.is_available():
            st.caption("Database unavailable — this upload is only saved for the current session.")

        with st.container(border=True):
            st.dataframe(new_df.head(8), width="stretch", height=220)
    except Exception as e:
        st.error(f"Parse failed: {e}")

# ============================================================
# Filters (drive KPIs + table below — dynamic state)
# ============================================================
st.markdown("---")
f1, f2, f3 = st.columns([2, 2, 3])
with f1:
    status_filter = st.multiselect(
        "Status", options=["cleaned", "needs_review", "error"],
        default=["cleaned", "needs_review", "error"],
        key="upload_status_filter",
    )
with f2:
    days_filter = st.selectbox("Window", options=[7, 14, 21, 30], index=2, format_func=lambda d: f"Last {d}d", key="upload_days_filter")
with f3:
    search = st.text_input("Search filename", placeholder="e.g. customer, vendor, payroll…", key="upload_search")

df = st.session_state.uploads_df.copy()
df = df[df["status"].isin(status_filter)]
df = df[df["uploaded_at"] >= datetime.now() - timedelta(days=days_filter)]
if search:
    df = df[df["filename"].str.contains(search, case=False, na=False)]

# ============================================================
# KPI row (computed live from filtered df)
# ============================================================
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total uploads", len(df))
k2.metric("Avg DQ score", f"{df['dq_score'].mean():.0f}" if len(df) else "—")
k3.metric("Pending review", int((df["status"] == "needs_review").sum()))
k4.metric("Errors", int((df["status"] == "error").sum()))
k5.metric("Avg missing %", f"{df['missing_pct'].mean():.1f}%" if len(df) else "—")

# ============================================================
# Charts — upload volume trend + status distribution
# ============================================================
c1, c2 = st.columns([2, 1])

with c1:
    with st.container(border=True):
        theme.eyebrow_header("Trend", "Upload volume — daily")
        trend = (
            df.assign(day=df["uploaded_at"].dt.date)
            .groupby("day").size().reset_index(name="count")
            .sort_values("day")
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=trend["day"], y=trend["count"],
            marker_color=theme.SUCCESS, marker_line_width=0,
        ))
        fig.update_layout(height=220, showlegend=False, bargap=0.35)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with c2:
    with st.container(border=True):
        theme.eyebrow_header("Breakdown", "Status distribution")
        status_counts = df["status"].value_counts()
        colors = {"cleaned": theme.SUCCESS, "needs_review": theme.WARNING, "error": theme.DANGER}
        fig2 = go.Figure(go.Pie(
            labels=status_counts.index, values=status_counts.values,
            hole=0.62,
            marker=dict(colors=[colors.get(s, theme.TEXT_MUTED) for s in status_counts.index]),
            textinfo="none",
        ))
        fig2.update_layout(height=220, showlegend=True, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig2, width="stretch", config={"displayModeBar": False})

# ============================================================
# Recent uploads — interactive data editor (inline review toggle)
# ============================================================
st.markdown("---")
theme.eyebrow_header("Table", "Recent uploads — inline review")

edited = st.data_editor(
    df.assign(uploaded_at=df["uploaded_at"].dt.strftime("%Y-%m-%d %H:%M")),
    width="stretch",
    hide_index=True,
    height=380,
    column_config={
        "filename": st.column_config.TextColumn("File", width="large"),
        "uploaded_at": st.column_config.TextColumn("Uploaded", width="medium"),
        "rows": st.column_config.NumberColumn("Rows", format="%d", width="small"),
        "columns": st.column_config.NumberColumn("Cols", format="%d", width="small"),
        "missing_pct": st.column_config.ProgressColumn(
            "Missing %", min_value=0, max_value=25, format="%.1f%%", width="medium"
        ),
        "duplicate_pct": st.column_config.ProgressColumn(
            "Dup %", min_value=0, max_value=10, format="%.1f%%", width="medium"
        ),
        "status": st.column_config.SelectboxColumn(
            "Status", options=["cleaned", "needs_review", "error"], width="medium"
        ),
        "dq_score": st.column_config.NumberColumn("DQ Score", format="%d", width="small"),
        "reviewed": st.column_config.CheckboxColumn("Reviewed", width="small"),
    },
    disabled=["filename", "uploaded_at", "rows", "columns", "missing_pct", "duplicate_pct", "dq_score"],
    key="uploads_editor",
)

st.caption(f"Showing {len(edited)} of {len(st.session_state.uploads_df)} total uploads · edits to Status/Reviewed persist for this session")