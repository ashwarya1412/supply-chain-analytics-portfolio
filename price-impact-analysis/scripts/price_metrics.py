"""
price_metrics.py

Loads retail_price.csv and adds derived, row-level metrics used for the
price/promotion impact analysis:

  - avg_competitor_price   : mean of comp_1, comp_2, comp_3
  - price_vs_competitor    : unit_price - avg_competitor_price
                             (positive = priced above competitors)
  - price_position         : "Above Market" / "At Market" / "Below Market"
                             based on price_vs_competitor vs. a small tolerance band
  - avg_competitor_freight : mean of fp1, fp2, fp3
  - freight_vs_competitor  : freight_price - avg_competitor_freight
  - revenue                : total_price (already qty * unit_price per the
                              dataset's own definition, kept as an explicit
                              alias for clarity in Tableau)
  - calendar context passed through as-is: weekday, weekend, holiday, month, year

Input:  data/raw/retail_price.csv
Output: outputs/price_metrics_enriched.csv   -- row-level, feeds category_price_summary.py
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

# Tolerance band (in the same currency unit as price) for calling something
# "At Market" rather than clearly above/below -- adjust if this doesn't fit
# the actual spread of your data once you see it printed below.
AT_MARKET_TOLERANCE = 5.0


def load_raw() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "retail_price.csv")


def add_competitor_metrics(df: pd.DataFrame) -> pd.DataFrame:
    comp_cols = ["comp_1", "comp_2", "comp_3"]
    fp_cols = ["fp1", "fp2", "fp3"]

    df["avg_competitor_price"] = df[comp_cols].mean(axis=1)
    df["price_vs_competitor"] = (df["unit_price"] - df["avg_competitor_price"]).round(2)

    def position(diff):
        if diff > AT_MARKET_TOLERANCE:
            return "Above Market"
        if diff < -AT_MARKET_TOLERANCE:
            return "Below Market"
        return "At Market"

    df["price_position"] = df["price_vs_competitor"].apply(position)

    df["avg_competitor_freight"] = df[fp_cols].mean(axis=1)
    df["freight_vs_competitor"] = (df["freight_price"] - df["avg_competitor_freight"]).round(2)

    return df


def add_revenue_alias(df: pd.DataFrame) -> pd.DataFrame:
    # total_price in this dataset already represents revenue (qty * unit_price);
    # aliasing it as "revenue" makes downstream Tableau fields self-explanatory.
    df["revenue"] = df["total_price"]
    return df


def main():
    df = load_raw()
    df = add_competitor_metrics(df)
    df = add_revenue_alias(df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "price_metrics_enriched.csv"
    df.to_csv(out_path, index=False)

    print(f"Rows processed: {len(df):,}")
    print(f"Categories: {df['product_category_name'].nunique():,}")
    print(f"\nPrice position breakdown:")
    print(df["price_position"].value_counts().to_string())
    print(f"\nPrice vs competitor -- min: {df['price_vs_competitor'].min():.2f}, "
          f"max: {df['price_vs_competitor'].max():.2f}, "
          f"mean: {df['price_vs_competitor'].mean():.2f}")
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
