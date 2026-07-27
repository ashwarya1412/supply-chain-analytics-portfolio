"""
vlt_calc.py

Calculates Vendor Lead Time (VLT) — the time between order purchase and
customer delivery — per seller, along with variance stats needed for
safety stock and reorder point calculations downstream.

Input:  data/raw/olist_orders_dataset.csv, data/raw/olist_order_items_dataset.csv
Output: outputs/vlt_by_vendor.csv
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def load_data() -> pd.DataFrame:
    orders = pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"],
    )
    order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")

    # Join orders to sellers via order_items (orders don't carry seller_id directly)
    df = order_items.merge(orders, on="order_id", how="inner")
    return df


def compute_vlt(df: pd.DataFrame) -> pd.DataFrame:
    # Only keep orders that were actually delivered (drop cancelled/undelivered — no VLT signal there)
    delivered = df.dropna(subset=["order_delivered_customer_date", "order_purchase_timestamp"]).copy()

    # VLT in days = delivery date - purchase date
    delivered["vlt_days"] = (
        delivered["order_delivered_customer_date"] - delivered["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # On-time flag: delivered on/before the estimated date
    delivered["on_time"] = delivered["order_delivered_customer_date"] <= delivered["order_estimated_delivery_date"]

    # Drop obviously bad rows (negative VLT = data error, or absurd outliers > 200 days)
    delivered = delivered[(delivered["vlt_days"] >= 0) & (delivered["vlt_days"] <= 200)]

    vendor_stats = (
        delivered.groupby("seller_id")
        .agg(
            order_count=("order_id", "nunique"),
            avg_vlt_days=("vlt_days", "mean"),
            vlt_std_dev=("vlt_days", "std"),
            on_time_rate=("on_time", "mean"),
        )
        .reset_index()
    )

    # Coefficient of variation — lets you compare variance across vendors regardless of their avg lead time
    vendor_stats["vlt_cv"] = vendor_stats["vlt_std_dev"] / vendor_stats["avg_vlt_days"]

    # Fill any NaN std dev (vendors with only 1 order have no variance) with 0
    vendor_stats["vlt_std_dev"] = vendor_stats["vlt_std_dev"].fillna(0)
    vendor_stats["vlt_cv"] = vendor_stats["vlt_cv"].fillna(0)

    # Exclude vendors with too few orders — lead time variance is statistically
    # meaningless below this threshold, and would otherwise falsely look "perfectly reliable" (std dev = 0)
    MIN_ORDER_COUNT = 3
    before_count = len(vendor_stats)
    vendor_stats = vendor_stats[vendor_stats["order_count"] >= MIN_ORDER_COUNT]
    dropped = before_count - len(vendor_stats)
    print(f"Excluded {dropped:,} vendors with fewer than {MIN_ORDER_COUNT} orders (variance not meaningful)")

    return vendor_stats.sort_values("order_count", ascending=False)


def main():
    df = load_data()
    vendor_stats = compute_vlt(df)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / "vlt_by_vendor.csv"
    vendor_stats.to_csv(out_path, index=False)

    print(f"Processed {len(df):,} order-item rows")
    print(f"Computed VLT stats for {len(vendor_stats):,} vendors")
    print(f"Saved to {out_path}")
    print("\nTop 5 vendors by order volume:")
    print(vendor_stats.head())


if __name__ == "__main__":
    main()
