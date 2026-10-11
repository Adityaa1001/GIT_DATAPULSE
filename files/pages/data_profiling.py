"""
DataPulse — Data Profiling page (multi-page: setup/nav/theme handled by app.py entry).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from modules import theme
from modules import mock_data

# ============================================================
# Dataset selector — pulls from Upload history if available
# ============================================================
theme.eyebrow_header("Stage 3 · Profiling", "Data Profiling")

fallback_files = ["customer_orders_q2.csv", "employee_master.xlsx", "vendor_ledger_2026.xlsx"]
available_files = (
    st.session_state["uploads_df"]["filename"].tolist()
    if "uploads_df" in st.session_state
    else fallback_files
)
selected_file = st.selectbox("Dataset", options=available_files, label_visibility="collapsed", key="dp_dataset_select")

# ============================================================
# Synthetic dataset (shared generator — same file, same data everywhere)
# ============================================================
df = mock_data.generate_dataset(selected_file)

# ============================================================
# Column-level profile table
# ============================================================
profile_rows = []
for col in df.columns:
    s = df[col]
    profile_rows.append({
        "column": col,
        "dtype": str(s.dtype),
        "missing_pct": round(s.isna().mean() * 100, 1),
        "unique_count": int(s.nunique(dropna=True)),
        "unique_pct": round(s.nunique(dropna=True) / len(s) * 100, 1),
    })
profile = pd.DataFrame(profile_rows)

# ============================================================
# KPI row
# ============================================================
total_rows = len(df)
total_cols = len(df.columns)
overall_missing_pct = df.isna().mean().mean() * 100
duplicate_rows = df.duplicated().sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total rows", f"{total_rows:,}")
k2.metric("Total columns", total_cols)
k3.metric("Avg missing %", f"{overall_missing_pct:.1f}%")
k4.metric("Duplicate rows", int(duplicate_rows))

# ============================================================
# Charts — dtype breakdown + missing % per column
# ============================================================
c1, c2 = st.columns([1, 2])

with c1:
    with st.container(border=True):
        theme.eyebrow_header("Breakdown", "Column types")
        dtype_counts = profile["dtype"].value_counts()
        fig1 = go.Figure(go.Pie(
            labels=dtype_counts.index, values=dtype_counts.values,
            hole=0.62, textinfo="none",
        ))
        fig1.update_layout(height=230, showlegend=True, legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
        st.plotly_chart(fig1, width='stretch', config={"displayModeBar": False})

with c2:
    with st.container(border=True):
        theme.eyebrow_header("Quality", "Missing values by column")
        sorted_profile = profile.sort_values("missing_pct", ascending=True)
        colors = [
            theme.DANGER if v > 15 else theme.WARNING if v > 0 else theme.SUCCESS
            for v in sorted_profile["missing_pct"]
        ]
        fig2 = go.Figure(go.Bar(
            x=sorted_profile["missing_pct"], y=sorted_profile["column"],
            orientation="h", marker_color=colors, marker_line_width=0,
        ))
        fig2.update_layout(height=230, showlegend=False, margin=dict(l=8, r=8, t=8, b=8))
        fig2.update_xaxes(title_text="Missing %", title_font=dict(size=10))
        st.plotly_chart(fig2, width='stretch', config={"displayModeBar": False})

# ============================================================
# Column profile table — interactive row selection
# ============================================================
st.markdown("---")
theme.eyebrow_header("Table", "Column profile — select a row to inspect")

event = st.dataframe(
    profile,
    width='stretch',
    hide_index=True,
    height=280,
    column_config={
        "column": st.column_config.TextColumn("Column", width="medium"),
        "dtype": st.column_config.TextColumn("Type", width="small"),
        "missing_pct": st.column_config.ProgressColumn("Missing %", min_value=0, max_value=100, format="%.1f%%"),
        "unique_pct": st.column_config.ProgressColumn("Unique %", min_value=0, max_value=100, format="%.1f%%"),
        "unique_count": st.column_config.NumberColumn("Unique count", format="%d"),
    },
    on_select="rerun",
    selection_mode="single-row",
)

selected_rows = event.selection.rows if event and event.selection else []
inspect_col = profile.iloc[selected_rows[0]]["column"] if selected_rows else profile.iloc[0]["column"]

# ============================================================
# Column inspector
# ============================================================
st.markdown("---")
theme.eyebrow_header("Inspector", f"Distribution — {inspect_col}")

col_series = df[inspect_col].dropna()
ic1, ic2 = st.columns([2, 1])

with ic1:
    with st.container(border=True):
        if pd.api.types.is_numeric_dtype(col_series):
            fig3 = go.Figure(go.Histogram(x=col_series, marker_color=theme.SUCCESS, nbinsx=30))
        elif pd.api.types.is_datetime64_any_dtype(col_series):
            fig3 = go.Figure(go.Histogram(x=col_series, marker_color=theme.SUCCESS, nbinsx=30))
        else:
            top_vals = col_series.astype(str).value_counts().head(8)
            fig3 = go.Figure(go.Bar(x=top_vals.index, y=top_vals.values, marker_color=theme.SUCCESS))
        fig3.update_layout(height=260, margin=dict(l=8, r=8, t=8, b=8))
        st.plotly_chart(fig3, width='stretch', config={"displayModeBar": False})

with ic2:
    row = profile[profile["column"] == inspect_col].iloc[0]
    with st.container(border=True):
        st.metric("Missing %", f"{row['missing_pct']}%")
    with st.container(border=True):
        st.metric("Unique values", f"{row['unique_count']:,}")
    if pd.api.types.is_numeric_dtype(col_series) and len(col_series):
        with st.container(border=True):
            st.metric("Mean", f"{col_series.mean():.2f}")
    elif len(col_series):
        top_val = col_series.astype(str).mode().iloc[0]
        with st.container(border=True):
            st.metric("Most common", top_val)

st.caption(f"Profiling {selected_file} · {total_rows:,} rows × {total_cols} columns · seed-generated preview data")