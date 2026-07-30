"""
category_price_summary.py

Rolls up price_metrics_enriched.csv into two summary tables for the
Tableau dashboard:

  1. category_price_summary.csv  -- one row per product_category_name
  2. product_price_summary.csv   -- one row per product_id (across all its
                                     monthly records), for a product-level
                                     drill-down / top-movers view

Metrics computed per group:
  - total_qty, total_revenue, avg_unit_price, avg_freight_price
  - avg_price_vs_competitor, avg_freight_vs_competitor
  - price_position breakdown (count of Above/At/Below Market records)
  - simple price-volume correlation (Pearson) where the group has enough
    variation to compute one -- a rough proxy for price elasticity direction
    (negative = higher price associated with lower qty, as classic demand
    theory would predict; positive = the opposite, worth flagging as
    unusual in the dashboard/README)
  - avg_product_score, avg_customers (demand-side context)
  - holiday_qty_share: % of total qty that occurred on holiday=1 rows,
    useful for seasonality framing

Input:  outputs/price_metrics_enriched.csv   (produced by price_metrics.py -- run that first)
Output: outputs/category_price_summary.csv
        outputs/product_price_summary.csv
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

MIN_ROWS_FOR_CORRELATION = 5  # below this, correlation is too noisy to trust


def load_enriched() -> pd.DataFrame:
    path = OUTPUT_DIR / "price_metrics_enriched.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- run price_metrics.py first.")
    return pd.read_csv(path)


def price_volume_correlation(group: pd.DataFrame) -> float:
    if len(group) < MIN_ROWS_FOR_CORRELATION:
        return float("nan")
    if group["unit_price"].nunique() < 2:
        return float("nan")
    return round(group["unit_price"].corr(group["qty"]), 3)


def summarize(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for key, group in df.groupby(group_col):
        position_counts = group["price_position"].value_counts()
        row = {
            group_col: key,
            "total_qty": group["qty"].sum(),
            "total_revenue": round(group["revenue"].sum(), 2),
            "avg_unit_price": round(group["unit_price"].mean(), 2),
            "avg_freight_price": round(group["freight_price"].mean(), 2),
            "avg_price_vs_competitor": round(group["price_vs_competitor"].mean(), 2),
            "avg_freight_vs_competitor": round(group["freight_vs_competitor"].mean(), 2),
            "above_market_count": int(position_counts.get("Above Market", 0)),
            "at_market_count": int(position_counts.get("At Market", 0)),
            "below_market_count": int(position_counts.get("Below Market", 0)),
            "price_volume_correlation": price_volume_correlation(group),
            "avg_product_score": round(group["product_score"].mean(), 2),
            "avg_customers": round(group["customers"].mean(), 2),
            "holiday_qty_share": round(
                group.loc[group["holiday"] == 1, "qty"].sum() / group["qty"].sum(), 4
            ) if group["qty"].sum() > 0 else 0,
            "record_count": len(group),
        }
        # Carry the category name through on product-level rows, so Tableau
        # doesn't need a join/blend to color or filter products by category.
        if group_col == "product_id":
            row["product_category_name"] = group["product_category_name"].iloc[0]
        rows.append(row)
    return pd.DataFrame(rows).sort_values("total_revenue", ascending=False)


def main():
    df = load_enriched()

    category_summary = summarize(df, "product_category_name")
    product_summary = summarize(df, "product_id")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    category_summary.to_csv(OUTPUT_DIR / "category_price_summary.csv", index=False)
    product_summary.to_csv(OUTPUT_DIR / "product_price_summary.csv", index=False)

    print("=== Category-Level Summary ===")
    print(f"Categories: {len(category_summary):,}")
    print(f"Total revenue across all categories: ${category_summary['total_revenue'].sum():,.2f}")
    print("\nPrice-volume correlation by category (negative = higher price, lower demand):")
    print(category_summary[["product_category_name", "price_volume_correlation"]].to_string(index=False))

    print("\n=== Product-Level Summary ===")
    print(f"Products: {len(product_summary):,}")
    print(f"Total revenue across all products: ${product_summary['total_revenue'].sum():,.2f}")

    print("\nSaved category_price_summary.csv and product_price_summary.csv to outputs/")


if __name__ == "__main__":
    main()
