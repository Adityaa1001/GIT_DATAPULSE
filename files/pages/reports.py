"""
DataPulse — Reports / Export page.
Real downloadable artifacts: cleaned dataset (CSV), a generated PDF
cleaning report, and a CSV audit log of every accept/reject action taken
on the Quality Score page.
"""

import streamlit as st
import pandas as pd

from modules import theme
from modules import mock_data
from modules import quality
from modules import reports

theme.eyebrow_header("Stage 6 · Export", "Reports / Export")

# ============================================================
# Dataset selector — same source as other pages
# ============================================================
fallback_files = ["customer_orders_q2.csv", "employee_master.xlsx", "vendor_ledger_2026.xlsx"]
available_files = (
    st.session_state["uploads_df"]["filename"].tolist()
    if "uploads_df" in st.session_state
    else fallback_files
)
selected_file = st.selectbox("Dataset", options=available_files, label_visibility="collapsed", key="reports_dataset_select")

# ============================================================
# Pull the same before/after state Dashboard and Quality Score use
# ============================================================
before_df = mock_data.generate_dataset(selected_file)
qs_cleaned = st.session_state.get("qs_cleaned_data", {})
qs_suggestions = st.session_state.get("qs_suggestions", {})
has_cleaning = selected_file in qs_cleaned

after_df = qs_cleaned[selected_file] if has_cleaning else before_df
suggestions = qs_suggestions.get(selected_file, [])

before_score = quality.compute_quality_score(before_df)
after_score = quality.compute_quality_score(after_df)

if not has_cleaning:
    st.info(
        f"No cleaning has been applied to **{selected_file}** yet. You can still export the raw dataset below — "
        "visit **Quality Score & AI Suggestions** first if you want the exported file and report to reflect cleaning fixes.",
        icon="ℹ️",
    )

# ============================================================
# Quick score recap
# ============================================================
r1, r2, r3 = st.columns(3)
r1.metric("Quality Score", f"{after_score['overall']:.0f}", delta=f"{after_score['overall'] - before_score['overall']:+.0f}")
r2.metric("Rows", f"{len(after_df):,}", delta=len(after_df) - len(before_df))
audit_log_all = st.session_state.get("audit_log", [])
audit_log_this_file = [a for a in audit_log_all if a["filename"] == selected_file]
r3.metric("Audit log entries", len(audit_log_this_file))

st.markdown("---")

# ============================================================
# Three export cards
# ============================================================
c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        theme.eyebrow_header("Export", "Cleaned dataset")
        st.caption(f"{len(after_df):,} rows × {len(after_df.columns)} columns, reflecting all accepted fixes.")
        csv_bytes = reports.dataframe_to_csv_bytes(after_df)
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"cleaned_{selected_file.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            key="download_cleaned_csv",
            type="primary",
        )

with c2:
    with st.container(border=True):
        theme.eyebrow_header("Export", "Cleaning report")
        st.caption("PDF summary: score comparison, sub-scores, and every suggestion reviewed.")
        pdf_bytes = reports.build_cleaning_report_pdf(
            filename=selected_file,
            before_score=before_score,
            after_score=after_score,
            before_rows=len(before_df),
            after_rows=len(after_df),
            suggestions=suggestions,
        )
        st.download_button(
            "Download PDF",
            data=pdf_bytes,
            file_name=f"cleaning_report_{selected_file.rsplit('.', 1)[0]}.pdf",
            mime="application/pdf",
            key="download_report_pdf",
            type="primary",
        )

with c3:
    with st.container(border=True):
        theme.eyebrow_header("Export", "Audit log")
        st.caption(f"{len(audit_log_this_file)} logged action(s) for this dataset this session.")
        if audit_log_this_file:
            audit_df = pd.DataFrame(audit_log_this_file)
            audit_csv = reports.dataframe_to_csv_bytes(audit_df)
        else:
            audit_csv = reports.dataframe_to_csv_bytes(pd.DataFrame(
                columns=["timestamp", "filename", "action", "column", "issue_type", "description", "fix_applied"]
            ))
        st.download_button(
            "Download CSV",
            data=audit_csv,
            file_name=f"audit_log_{selected_file.rsplit('.', 1)[0]}.csv",
            mime="text/csv",
            key="download_audit_csv",
            type="primary",
            disabled=len(audit_log_this_file) == 0,
        )

# ============================================================
# Audit log preview table
# ============================================================
st.markdown("---")
theme.eyebrow_header("Table", "Audit log preview")

if not audit_log_this_file:
    st.caption("No actions logged yet for this dataset — accept or reject a suggestion on the Quality Score page to populate this.")
else:
    audit_df_display = pd.DataFrame(audit_log_this_file).sort_values("timestamp", ascending=False)
    st.dataframe(
        audit_df_display,
        width="stretch",
        hide_index=True,
        height=min(320, 44 + 36 * len(audit_df_display)),
        column_config={
            "timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
            "filename": st.column_config.TextColumn("File", width="medium"),
            "action": st.column_config.TextColumn("Action", width="small"),
            "column": st.column_config.TextColumn("Column", width="small"),
            "issue_type": st.column_config.TextColumn("Issue", width="small"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "fix_applied": st.column_config.TextColumn("Fix applied", width="large"),
        },
    )

st.caption(f"Working on {selected_file} · exports reflect the current session state · PDF generated on demand")