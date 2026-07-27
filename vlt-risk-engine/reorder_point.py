"""
reorder_point.py

Calculates the Reorder Point (ROP) per vendor — the inventory level at
which a new order should be triggered to avoid stockouts before the
next delivery arrives.

Formula:
    ROP = (avg_daily_demand * avg_lead_time_days) + safety_stock_units

Input:  outputs/safety_stock_by_vendor.csv   (produced by safety_stock.py — run that first)
Output: outputs/reorder_point_by_vendor.csv
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def load_safety_stock() -> pd.DataFrame:
    path = OUTPUT_DIR / "safety_stock_by_vendor.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — run safety_stock.py first, it produces the input this script needs."
        )
    return pd.read_csv(path)


def compute_reorder_point(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Demand during lead time = how many units will sell before the next order arrives
    df["demand_during_lead_time"] = df["avg_daily_demand"] * df["avg_vlt_days"]

    # ROP = demand expected during the lead time window + the safety buffer
    df["reorder_point_units"] = df["demand_during_lead_time"] + df["safety_stock_units"]
    df["reorder_point_units"] = df["reorder_point_units"].round(0)

    # Max stock level — a useful upper bound for review, roughly ROP + one demand cycle
    df["max_stock_level_units"] = df["reorder_point_units"] + (df["avg_daily_demand"] * df["avg_vlt_days"])
    df["max_stock_level_units"] = df["max_stock_level_units"].round(0)

    return df.sort_values("reorder_point_units", ascending=False)


def main():
    df = load_safety_stock()
    result = compute_reorder_point(df)

    out_path = OUTPUT_DIR / "reorder_point_by_vendor.csv"
    result.to_csv(out_path, index=False)

    print(f"Computed reorder points for {len(result):,} vendors")
    print(f"Saved to {out_path}")
    print("\nTop 5 vendors by reorder point (need the biggest on-hand buffer before reordering):")
    print(
        result[
            [
                "seller_id",
                "avg_vlt_days",
                "avg_daily_demand",
                "safety_stock_units",
                "reorder_point_units",
                "max_stock_level_units",
            ]
        ].head()
    )


if __name__ == "__main__":
    main()
