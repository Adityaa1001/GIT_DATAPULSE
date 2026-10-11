"""
Shared synthetic dataset generator for DataPulse's demo/mock screens.
Deterministic per filename (same seed -> same data), so Data Profiling,
Quality Score, and Dashboard all agree on what a given uploaded file
"contains" without needing real file storage yet.
"""

import numpy as np
import pandas as pd

REGIONS = ["North", "South", "East", "West", "Central"]
STATUSES = ["active", "pending", "closed", "cancelled"]
FIRST_NAMES = ["Aditya", "Priya", "Rahul", "Sara", "Kabir", "Meera", "Zoya", "Arjun", "Neha", "Ishaan"]
LAST_NAMES = ["Sharma", "Patel", "Reddy", "Nair", "Iyer", "Khan", "Gupta", "Verma", "Rao", "Menon"]


def generate_dataset(filename: str) -> pd.DataFrame:
    """Generates a realistic, deterministic synthetic dataset for a given
    filename. Same filename always produces the same data within a run."""
    seed = abs(hash(filename)) % (2**32)
    rng = np.random.default_rng(seed=seed)
    n_rows = int(rng.integers(300, 900))

    customer_names = rng.choice(
        [f"{f} {l}" for f in FIRST_NAMES for l in LAST_NAMES], size=n_rows
    )
    raw = pd.DataFrame({
        "order_id": np.arange(100000, 100000 + n_rows),
        "customer_name": customer_names,
        "email": [
            f"{n.split()[0].lower()}.{n.split()[1].lower()}@example.com" if rng.random() > 0.08 else None
            for n in customer_names
        ],
        "signup_date": pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 600, n_rows), unit="D"),
        "amount": np.where(rng.random(n_rows) > 0.05, np.round(rng.gamma(3, 45, n_rows), 2), np.nan),
        "region": rng.choice(REGIONS, n_rows),
        "status": rng.choice(STATUSES, n_rows, p=[0.5, 0.2, 0.2, 0.1]),
        "discount_pct": np.where(rng.random(n_rows) > 0.15, np.round(rng.uniform(0, 30, n_rows), 1), np.nan),
        "is_returning": rng.choice([True, False], n_rows, p=[0.35, 0.65]),
    })
    # inject some duplicate rows for realism
    dup_idx = rng.choice(raw.index, size=max(1, int(n_rows * 0.03)), replace=False)
    raw = pd.concat([raw, raw.loc[dup_idx]], ignore_index=True)

    # inject a handful of extreme outliers in 'amount' for realism
    outlier_idx = rng.choice(raw.index, size=max(1, int(len(raw) * 0.01)), replace=False)
    raw.loc[outlier_idx, "amount"] = raw.loc[outlier_idx, "amount"] * rng.uniform(6, 12, len(outlier_idx))

    return raw