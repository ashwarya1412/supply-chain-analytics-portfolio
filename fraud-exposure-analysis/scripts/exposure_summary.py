"""
exposure_summary.py

Rolls up flagged_orders.csv (order-level) into two risk summary tables:
  - seller-level risk (outputs/seller_risk_summary.csv)
  - category-level risk (outputs/category_risk_summary.csv)

An order can contain items from multiple sellers/categories, so exposure
is allocated proportionally: each order-item gets a share of the order's
exposure equal to that item's share of the order's total item value.
This avoids double-counting the full order exposure against every seller
that touched a multi-seller order.

Risk Tier thresholds (applied to both seller and category tables):
    High Risk:   risk_rate >= 20%
    Medium Risk: risk_rate >= 10%
    Low Risk:    risk_rate < 10%
(Adjust thresholds if they don't fit your data's distribution --
 check the printed percentile summary before finalizing.)

Input:
    outputs/flagged_orders.csv          (produced by risk_flagging.py -- run that first)
    data/raw/olist_order_items_dataset.csv
    data/raw/olist_products_dataset.csv (for product_category_name)

Output:
    outputs/seller_risk_summary.csv
    outputs/category_risk_summary.csv
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

HIGH_RISK_THRESHOLD = 0.20
MEDIUM_RISK_THRESHOLD = 0.10


def load_flagged_orders() -> pd.DataFrame:
    path = OUTPUT_DIR / "flagged_orders.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- run risk_flagging.py first.")
    return pd.read_csv(path)


def load_order_items_with_category() -> pd.DataFrame:
    items = pd.read_csv(
        DATA_DIR / "olist_order_items_dataset.csv",
        usecols=["order_id", "order_item_id", "product_id", "seller_id", "price"],
    )
    products = pd.read_csv(
        DATA_DIR / "olist_products_dataset.csv",
        usecols=["product_id", "product_category_name"],
    )
    return items.merge(products, on="product_id", how="left")


def allocate_exposure(flagged: pd.DataFrame, items: pd.DataFrame) -> pd.DataFrame:
    df = items.merge(
        flagged[["order_id", "is_risk_flag", "risk_reason", "exposure_usd"]],
        on="order_id",
        how="left",
    )

    # Each item's share of its order's total item value (price)
    order_item_totals = df.groupby("order_id")["price"].transform("sum")
    df["item_share"] = (df["price"] / order_item_totals).fillna(0)
    df["allocated_exposure_usd"] = (df["item_share"] * df["exposure_usd"]).round(2)

    return df


def risk_tier(risk_rate: float) -> str:
    if risk_rate >= HIGH_RISK_THRESHOLD:
        return "High Risk"
    if risk_rate >= MEDIUM_RISK_THRESHOLD:
        return "Medium Risk"
    return "Low Risk"


def summarize(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    flagged_order_ids = df.loc[df["is_risk_flag"] == True, ["order_id"]].drop_duplicates()
    flagged_order_ids["_flagged"] = 1

    summary = df.groupby(group_col).agg(
        total_orders=("order_id", "nunique"),
        total_exposure_usd=("allocated_exposure_usd", "sum"),
    ).reset_index()

    # Count distinct flagged orders per group (not per item row)
    flagged_counts = (
        df[df["is_risk_flag"] == True]
        .groupby(group_col)["order_id"]
        .nunique()
        .reset_index(name="flagged_orders")
    )
    summary = summary.merge(flagged_counts, on=group_col, how="left")
    summary["flagged_orders"] = summary["flagged_orders"].fillna(0).astype(int)

    summary["risk_rate"] = (summary["flagged_orders"] / summary["total_orders"]).round(4)
    summary["total_exposure_usd"] = summary["total_exposure_usd"].round(2)
    summary["risk_tier"] = summary["risk_rate"].apply(risk_tier)

    return summary.sort_values("total_exposure_usd", ascending=False)


def main():
    flagged = load_flagged_orders()
    items = load_order_items_with_category()

    allocated = allocate_exposure(flagged, items)

    seller_summary = summarize(allocated, "seller_id")
    category_summary = summarize(allocated, "product_category_name")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seller_summary.to_csv(OUTPUT_DIR / "seller_risk_summary.csv", index=False)
    category_summary.to_csv(OUTPUT_DIR / "category_risk_summary.csv", index=False)

    print("=== Seller-Level Summary ===")
    print(f"Sellers: {len(seller_summary):,}")
    print(seller_summary["risk_tier"].value_counts().to_string())
    print(f"Total exposure: ${seller_summary['total_exposure_usd'].sum():,.2f}")

    print("\n=== Category-Level Summary ===")
    print(f"Categories: {len(category_summary):,}")
    print(category_summary["risk_tier"].value_counts().to_string())
    print(f"Total exposure: ${category_summary['total_exposure_usd'].sum():,.2f}")

    print("\nSaved seller_risk_summary.csv and category_risk_summary.csv to outputs/")


if __name__ == "__main__":
    main()