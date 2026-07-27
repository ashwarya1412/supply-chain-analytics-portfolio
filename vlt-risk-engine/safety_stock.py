"""
safety_stock.py

Calculates average daily demand per vendor and applies the safety stock
formula using the VLT variance computed in vlt_calc.py.

Formula:
    Safety Stock (SS) = Z * sigma_LT * avg_daily_demand
    Z = 1.65 for a 95% service level (change SERVICE_LEVEL_Z below for 90%/99%)

Input:  data/raw/olist_orders_dataset.csv, data/raw/olist_order_items_dataset.csv
        outputs/vlt_by_vendor.csv   (produced by vlt_calc.py — run that first)
Output: outputs/safety_stock_by_vendor.csv
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Z-scores for common service levels — swap this to change your target service level
SERVICE_LEVEL_Z = 1.65  # 95% service level. Use 1.28 for 90%, 2.33 for 99%.


def load_vlt_stats() -> pd.DataFrame:
    vlt_path = OUTPUT_DIR / "vlt_by_vendor.csv"
    if not vlt_path.exists():
        raise FileNotFoundError(
            f"{vlt_path} not found — run vlt_calc.py first, it produces the input this script needs."
        )
    return pd.read_csv(vlt_path)


def compute_avg_daily_demand() -> pd.DataFrame:
    orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp"])
    order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")

    df = order_items.merge(orders[["order_id", "order_purchase_timestamp"]], on="order_id", how="inner")
    df["order_date"] = df["order_purchase_timestamp"].dt.date

    # Total units sold per vendor (each row in order_items = 1 unit of a product)
    vendor_totals = df.groupby("seller_id").agg(total_units=("order_item_id", "count")).reset_index()

    # Active selling window per vendor = days between their first and last order
    # (better than dividing by the whole dataset's date range, which would understate demand for newer vendors)
    date_range = df.groupby("seller_id")["order_date"].agg(["min", "max"]).reset_index()
    date_range["active_days"] = (pd.to_datetime(date_range["max"]) - pd.to_datetime(date_range["min"])).dt.days + 1

    demand = vendor_totals.merge(date_range[["seller_id", "active_days"]], on="seller_id")
    demand["avg_daily_demand"] = demand["total_units"] / demand["active_days"]

    return demand[["seller_id", "total_units", "active_days", "avg_daily_demand"]]


def compute_safety_stock(vlt_stats: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    merged = vlt_stats.merge(demand, on="seller_id", how="inner")

    merged["safety_stock_units"] = (
        SERVICE_LEVEL_Z * merged["vlt_std_dev"] * merged["avg_daily_demand"]
    )

    # Round to whole units — you can't stock half an item
    merged["safety_stock_units"] = merged["safety_stock_units"].round(0)

    return merged.sort_values("safety_stock_units", ascending=False)


def main():
    vlt_stats = load_vlt_stats()
    demand = compute_avg_daily_demand()
    result = compute_safety_stock(vlt_stats, demand)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / "safety_stock_by_vendor.csv"
    result.to_csv(out_path, index=False)

    print(f"Service level target: {SERVICE_LEVEL_Z} Z-score")
    print(f"Computed safety stock for {len(result):,} vendors")
    print(f"Saved to {out_path}")
    print("\nTop 5 vendors by safety stock required (highest risk buffer needed):")
    print(result[["seller_id", "avg_vlt_days", "vlt_std_dev", "avg_daily_demand", "safety_stock_units"]].head())


if __name__ == "__main__":
    main()
