from __future__ import annotations

from pathlib import Path

import pandas as pd


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROFILES_PATH = RAW_DIR / "credit_monitoring_profiles.csv"

SAMPLE_PROFILES = [
    {
        "customer_id": "MON-1001",
        "name": "Ana Souza",
        "current_score": 742,
        "previous_score": 751,
        "credit_utilization_pct": 31,
        "previous_utilization_pct": 24,
        "recent_late_payments": 0,
        "previous_late_payments": 0,
        "negative_records": 0,
        "hard_inquiries_3m": 1,
        "monthly_income": 12500,
        "exposure": 18000,
        "segment": "Prime",
    },
    {
        "customer_id": "MON-1002",
        "name": "Bruno Lima",
        "current_score": 618,
        "previous_score": 662,
        "credit_utilization_pct": 72,
        "previous_utilization_pct": 54,
        "recent_late_payments": 2,
        "previous_late_payments": 1,
        "negative_records": 1,
        "hard_inquiries_3m": 4,
        "monthly_income": 7300,
        "exposure": 24600,
        "segment": "Mass Affluent",
    },
    {
        "customer_id": "MON-1003",
        "name": "Carla Mendes",
        "current_score": 556,
        "previous_score": 603,
        "credit_utilization_pct": 89,
        "previous_utilization_pct": 77,
        "recent_late_payments": 4,
        "previous_late_payments": 2,
        "negative_records": 2,
        "hard_inquiries_3m": 5,
        "monthly_income": 5200,
        "exposure": 28100,
        "segment": "Mass Market",
    },
    {
        "customer_id": "MON-1004",
        "name": "Daniela Rocha",
        "current_score": 684,
        "previous_score": 679,
        "credit_utilization_pct": 38,
        "previous_utilization_pct": 41,
        "recent_late_payments": 0,
        "previous_late_payments": 0,
        "negative_records": 0,
        "hard_inquiries_3m": 1,
        "monthly_income": 9800,
        "exposure": 13200,
        "segment": "Prime",
    },
]


def ensure_sample_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILES_PATH.exists():
        pd.DataFrame(SAMPLE_PROFILES).to_csv(PROFILES_PATH, index=False)


def load_profiles() -> pd.DataFrame:
    ensure_sample_data()
    return pd.read_csv(PROFILES_PATH)
