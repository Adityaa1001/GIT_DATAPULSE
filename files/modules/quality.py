"""
Shared rule-based quality-detection logic for DataPulse.
Used by both the Quality Score page (accept/reject workflow) and the
Dashboard page (before/after comparison), so scoring stays consistent
everywhere it's shown.
"""

import pandas as pd
import numpy as np


def generate_suggestions(df: pd.DataFrame) -> list:
    suggestions = []
    sid = 0

    # --- missing values, per column ---
    for col in df.columns:
        s = df[col]
        missing_count = int(s.isna().sum())
        if missing_count == 0:
            continue
        missing_pct = round(missing_count / len(df) * 100, 1)
        if pd.api.types.is_numeric_dtype(s):
            fill_value = round(float(s.median()), 2)
            fix_desc = f"Fill missing values with the column median ({fill_value})"
        else:
            mode = s.mode(dropna=True)
            fill_value = mode.iloc[0] if len(mode) else "Unknown"
            fix_desc = f"Fill missing values with the most common value ('{fill_value}')"
        suggestions.append({
            "id": f"sugg_{sid}", "column": col, "issue_type": "missing",
            "description": f"{missing_count} missing values ({missing_pct}%) in '{col}'",
            "fix_description": fix_desc,
            "fill_value": fill_value,
            "status": "pending",
        })
        sid += 1

    # --- duplicate rows, whole-table ---
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        suggestions.append({
            "id": f"sugg_{sid}", "column": "(all columns)", "issue_type": "duplicate",
            "description": f"{dup_count} fully duplicate rows detected",
            "fix_description": "Remove duplicate rows, keep the first occurrence",
            "status": "pending",
        })
        sid += 1

    # --- outliers, per numeric column (Z-score) ---
    for col in df.select_dtypes(include=[np.number]).columns:
        s = df[col].dropna()
        if len(s) < 5 or s.std(ddof=0) == 0:
            continue
        z = (s - s.mean()) / s.std(ddof=0)
        outlier_count = int((z.abs() > 3).sum())
        if outlier_count > 0:
            suggestions.append({
                "id": f"sugg_{sid}", "column": col, "issue_type": "outlier",
                "description": f"{outlier_count} statistical outliers in '{col}' (|z| > 3)",
                "fix_description": "Cap outlier values to within 3 standard deviations of the mean",
                "status": "pending",
            })
            sid += 1

    return suggestions


def apply_suggestion(df: pd.DataFrame, suggestion: dict) -> pd.DataFrame:
    df = df.copy()
    col = suggestion["column"]
    if suggestion["issue_type"] == "missing":
        df[col] = df[col].fillna(suggestion["fill_value"])
    elif suggestion["issue_type"] == "duplicate":
        df = df.drop_duplicates(keep="first").reset_index(drop=True)
    elif suggestion["issue_type"] == "outlier":
        s = df[col]
        mean, std = s.mean(), s.std(ddof=0)
        lower, upper = mean - 3 * std, mean + 3 * std
        df[col] = s.clip(lower, upper)
    return df


def compute_quality_score(df: pd.DataFrame) -> dict:
    completeness = 100 - df.isna().mean().mean() * 100
    uniqueness = 100 - (df.duplicated().sum() / len(df) * 100 if len(df) else 0)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols):
        valid_fracs = []
        for col in numeric_cols:
            s = df[col].dropna()
            if len(s) < 5 or s.std(ddof=0) == 0:
                valid_fracs.append(1.0)
                continue
            z = (s - s.mean()) / s.std(ddof=0)
            valid_fracs.append(float((z.abs() <= 3).mean()))
        validity = float(np.mean(valid_fracs)) * 100
    else:
        validity = 100.0

    consistency = 100.0
    email_cols = [c for c in df.columns if c.lower() == "email"]
    if email_cols:
        s = df[email_cols[0]].dropna().astype(str)
        if len(s):
            valid_email = s.str.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
            consistency = float(valid_email.mean()) * 100

    overall = round(0.30 * completeness + 0.25 * uniqueness + 0.25 * validity + 0.20 * consistency, 1)
    return {
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "validity": round(validity, 1),
        "consistency": round(consistency, 1),
        "overall": overall,
    }