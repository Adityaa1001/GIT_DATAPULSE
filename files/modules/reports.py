"""
Report generation for DataPulse's Reports/Export page.
Builds a real PDF cleaning report (fpdf2) plus CSV export bytes for the
cleaned dataset and audit log — actual downloadable artifacts, not stubs.
"""

import io
from datetime import datetime

import pandas as pd
from fpdf import FPDF


def _ascii_safe(text) -> str:
    """FPDF's core fonts only support latin-1. Any character outside that
    range (smart quotes, em-dashes, emoji, etc.) gets swapped for a safe
    ASCII equivalent instead of crashing PDF generation."""
    text = str(text)
    replacements = {
        "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_cleaning_report_pdf(
    filename: str,
    before_score: dict,
    after_score: dict,
    before_rows: int,
    after_rows: int,
    suggestions: list,
) -> bytes:
    """Builds a one-to-two-page PDF summarizing the cleaning run for a
    dataset: score comparison, sub-scores, and every suggestion with its
    accept/reject outcome."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # --- Header ---
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(15, 110, 86)
    pdf.cell(0, 10, "DataPulse - Cleaning Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 6, f"Dataset: {_ascii_safe(filename)}", ln=True)
    pdf.ln(4)

    # --- Score summary ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "Quality Score Summary", ln=True)
    pdf.set_draw_color(220, 220, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(40, 40, 40)
    delta = after_score["overall"] - before_score["overall"]
    pdf.cell(0, 7, f"Overall Score: {before_score['overall']:.0f} -> {after_score['overall']:.0f}  ({'+' if delta >= 0 else ''}{delta:.0f} pts)", ln=True)
    pdf.cell(0, 7, f"Row count: {before_rows:,} -> {after_rows:,}", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Sub-scores (Before -> After)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for label, key in [("Completeness", "completeness"), ("Uniqueness", "uniqueness"),
                        ("Validity", "validity"), ("Consistency", "consistency")]:
        pdf.cell(0, 6, f"  {label}: {before_score[key]:.1f}%  ->  {after_score[key]:.1f}%", ln=True)
    pdf.ln(4)

    # --- Suggestions table ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "AI Suggestions Reviewed", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    if not suggestions:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "No issues were detected in this dataset.", ln=True)
    else:
        for s in suggestions:
            status = s.get("status", "pending")
            color = {"accepted": (15, 122, 71), "rejected": (179, 38, 30), "pending": (150, 150, 150)}[status]
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*color)
            pdf.cell(0, 6, _ascii_safe(f"[{status.upper()}] {s['description']}"), ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 5, _ascii_safe(f"    Suggested fix: {s['fix_description']}"))
            pdf.ln(1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 140, 140)
    pdf.multi_cell(0, 5, "Suggestions are generated using rule-based statistics (missing-value counts, "
                          "duplicate detection, Z-score outlier analysis) - not a trained ML model. "
                          "All fixes shown as ACCEPTED were applied to the exported cleaned dataset.")

    return bytes(pdf.output())