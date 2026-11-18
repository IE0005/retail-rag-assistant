"""Generate one markdown profile document per store from the real sales data.

These documents are the "grounded in actual data" half of the knowledge
base (the hand-written docs in knowledge_base/docs/ are the "policy and
glossary" half). Run this once before first ingesting the knowledge base,
and again any time the underlying CSVs change.

    python scripts/build_store_profiles.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "knowledge_base" / "docs" / "store_profiles"

TYPE_LABELS = {"A": "large-format (Type A)", "B": "mid-size (Type B)", "C": "small-format (Type C)"}


def fmt_usd(value: float) -> str:
    return f"-${abs(value):,.0f}" if value < 0 else f"${value:,.0f}"


def load_merged() -> pd.DataFrame:
    train = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["Date"])
    features = pd.read_csv(DATA_DIR / "features.csv", parse_dates=["Date"])
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    df = train.merge(features, on=["Store", "Date", "IsHoliday"], how="inner")
    df = df.merge(stores, on="Store", how="inner")
    return df


def describe_trend(dept_weekly: pd.Series) -> str:
    dept_weekly = dept_weekly.sort_index()
    if len(dept_weekly) < 10:
        return "insufficient history to characterize a trend"
    half = len(dept_weekly) // 2
    first_half_avg = dept_weekly.iloc[:half].mean()
    second_half_avg = dept_weekly.iloc[half:].mean()
    if first_half_avg == 0:
        return "insufficient history to characterize a trend"
    pct_change = (second_half_avg - first_half_avg) / first_half_avg * 100
    if pct_change > 10:
        return f"climbing (+{pct_change:.0f}% from the first half of its history to the second half)"
    if pct_change < -10:
        return f"declining ({pct_change:.0f}% from the first half of its history to the second half)"
    return "roughly flat across its history"


def build_store_doc(store_id: int, store_df: pd.DataFrame) -> str:
    store_type = store_df["Type"].iloc[0]
    size = int(store_df["Size"].iloc[0])

    weekly_total = store_df.groupby("Date")["Weekly_Sales"].sum()
    holiday_weekly = store_df[store_df["IsHoliday"]].groupby("Date")["Weekly_Sales"].sum()
    non_holiday_weekly = store_df[~store_df["IsHoliday"]].groupby("Date")["Weekly_Sales"].sum()

    dept_avg = store_df.groupby("Dept")["Weekly_Sales"].mean().sort_values(ascending=False)
    top_depts = dept_avg.head(5)
    bottom_depts = dept_avg.tail(3)

    holiday_ratio = (
        holiday_weekly.mean() / non_holiday_weekly.mean()
        if len(holiday_weekly) and len(non_holiday_weekly) and non_holiday_weekly.mean() > 0
        else float("nan")
    )

    trend = describe_trend(weekly_total)

    lines = [
        f"# Store {store_id} Profile",
        "",
        f"Store {store_id} is a {TYPE_LABELS.get(store_type, store_type)} store, "
        f"{size:,} square feet.",
        "",
        f"## Overall sales",
        "",
        f"- Average total weekly sales across all departments: ${weekly_total.mean():,.0f}",
        f"- Weeks of history available: {len(weekly_total)}",
        f"- Overall sales trend: {trend}",
    ]

    if not np.isnan(holiday_ratio):
        lines += [
            f"- Holiday weeks average ${holiday_weekly.mean():,.0f} vs. ${non_holiday_weekly.mean():,.0f} "
            f"on non-holiday weeks — a {holiday_ratio:.1f}x holiday lift.",
        ]

    lines += [
        "",
        "## Top-performing departments (by average weekly sales)",
        "",
    ]
    for dept, val in top_depts.items():
        lines.append(f"- Dept {int(dept)}: {fmt_usd(val)}/week average")

    lines += [
        "",
        "## Lowest-performing departments (by average weekly sales)",
        "",
    ]
    for dept, val in bottom_depts.items():
        lines.append(f"- Dept {int(dept)}: {fmt_usd(val)}/week average")

    return "\n".join(lines) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_merged()

    stores = sorted(df["Store"].unique())
    print(f"Generating profiles for {len(stores)} stores...")
    for store_id in stores:
        store_df = df[df["Store"] == store_id]
        doc = build_store_doc(int(store_id), store_df)
        out_path = OUT_DIR / f"store_{store_id:02d}.md"
        out_path.write_text(doc)

    print(f"Wrote {len(stores)} store profile documents to {OUT_DIR}")


if __name__ == "__main__":
    main()
