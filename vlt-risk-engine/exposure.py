"""
exposure.py

Calculates the financial exposure ($ at risk) per vendor — the estimated
revenue lost if a vendor's inventory runs out before their lead time
completes, based on historical avg selling price.

Formula:
    Stockout Risk Units = MAX(0, Demand During Lead Time - Safety Stock)
        (a rough proxy: how much demand isn't covered by the safety buffer,
         i.e. the units at risk of being unavailable in a bad lead-time cycle)
    Stockout Exposure ($) = Stockout Risk Units * Avg Selling Price
    Margin at Risk ($) = Stockout Exposure ($) * Assumed Gross Margin %

Input:  outputs/reorder_point_by_vendor.csv   (produced by reorder_point.py — run that first)
        data/raw/olist_order_items_dataset.csv (for avg selling price per vendor)
Output: outputs/vendor_risk_summary.csv   <-- this is the final file for Excel/Tableau
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Assumed gross margin — adjust if you find/assume a more realistic figure for e-commerce
ASSUMED_GROSS_MARGIN = 0.30


def load_reorder_data() -> pd.DataFrame:
    path = OUTPUT_DIR / "reorder_point_by_vendor.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — run reorder_point.py first, it produces the input this script needs."
        )
    return pd.read_csv(path)


def compute_avg_selling_price() -> pd.DataFrame:
    order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
    price_by_vendor = order_items.groupby("seller_id").agg(avg_selling_price=("price", "mean")).reset_index()
    return price_by_vendor


def compute_exposure(df: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    df = df.merge(prices, on="seller_id", how="left")

    # Units at risk = demand expected during lead time that safety stock doesn't cover
    df["stockout_risk_units"] = (df["demand_during_lead_time"] - df["safety_stock_units"]).clip(lower=0)

    df["stockout_exposure_usd"] = (df["stockout_risk_units"] * df["avg_selling_price"]).round(2)
    df["margin_at_risk_usd"] = (df["stockout_exposure_usd"] * ASSUMED_GROSS_MARGIN).round(2)

    # Simple risk tier for dashboard filtering/coloring
    def risk_tier(row):
        if row["on_time_rate"] < 0.85 or row["vlt_cv"] > 0.75:
            return "High Risk"
        elif row["on_time_rate"] < 0.92 or row["vlt_cv"] > 0.5:
            return "Medium Risk"
        return "Low Risk"

    df["risk_tier"] = df.apply(risk_tier, axis=1)

    return df.sort_values("stockout_exposure_usd", ascending=False)


def main():
    df = load_reorder_data()
    prices = compute_avg_selling_price()
    result = compute_exposure(df, prices)

    out_path = OUTPUT_DIR / "vendor_risk_summary.csv"
    result.to_csv(out_path, index=False)

    print(f"Assumed gross margin: {ASSUMED_GROSS_MARGIN:.0%}")
    print(f"Computed financial exposure for {len(result):,} vendors")
    print(f"Saved final summary to {out_path}")
    print(f"\nTotal stockout exposure across all vendors: ${result['stockout_exposure_usd'].sum():,.2f}")
    print(f"Vendors flagged High Risk: {(result['risk_tier'] == 'High Risk').sum():,}")
    print("\nTop 5 vendors by financial exposure:")
    print(
        result[
            ["seller_id", "risk_tier", "on_time_rate", "vlt_cv", "stockout_risk_units", "stockout_exposure_usd", "margin_at_risk_usd"]
        ].head()
    )


if __name__ == "__main__":
    main()
