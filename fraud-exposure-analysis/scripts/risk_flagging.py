"""
risk_flagging.py

Flags orders as "at risk" using two proxy signals (Olist has no labeled
fraud field, so these are reasonable stand-ins for fraud/mishandled orders):

  1. Order status = canceled or unavailable  -> reason: "canceled"
  2. Order status = delivered AND review_score <= 2 -> reason: "low_review"

For each flagged order, financial exposure = total payment value for that
order (summed across installments/payment rows).

Input:
    data/raw/olist_orders_dataset.csv
    data/raw/olist_order_reviews_dataset.csv
    data/raw/olist_order_payments_dataset.csv
    data/raw/olist_order_items_dataset.csv   (for product_category via product_id join,
                                               used later in exposure_summary.py)

Output:
    outputs/flagged_orders.csv   -- one row per order, with is_risk_flag,
                                     risk_reason, and exposure_usd
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

LOW_REVIEW_THRESHOLD = 2  # review_score <= this counts as "suspiciously low"
CANCELED_STATUSES = {"canceled", "unavailable"}


def load_orders() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        usecols=["order_id", "order_status", "customer_id", "order_purchase_timestamp"],
    )


def load_reviews() -> pd.DataFrame:
    reviews = pd.read_csv(
        DATA_DIR / "olist_order_reviews_dataset.csv",
        usecols=["order_id", "review_score"],
    )
    # An order can have multiple review rows (resubmissions) -- keep the lowest
    # score per order, since that's the worst signal a customer gave.
    return reviews.groupby("order_id", as_index=False)["review_score"].min()


def load_payment_value() -> pd.DataFrame:
    payments = pd.read_csv(
        DATA_DIR / "olist_order_payments_dataset.csv",
        usecols=["order_id", "payment_value"],
    )
    return payments.groupby("order_id", as_index=False)["payment_value"].sum()


def flag_orders(orders: pd.DataFrame, reviews: pd.DataFrame, payments: pd.DataFrame) -> pd.DataFrame:
    df = orders.merge(reviews, on="order_id", how="left")
    df = df.merge(payments, on="order_id", how="left")
    df["payment_value"] = df["payment_value"].fillna(0)

    is_canceled = df["order_status"].isin(CANCELED_STATUSES)
    is_low_review = (df["order_status"] == "delivered") & (df["review_score"] <= LOW_REVIEW_THRESHOLD)

    df["is_risk_flag"] = is_canceled | is_low_review

    def reason(row):
        if row["order_status"] in CANCELED_STATUSES:
            return "canceled"
        if row["order_status"] == "delivered" and row["review_score"] <= LOW_REVIEW_THRESHOLD:
            return "low_review"
        return "none"

    df["risk_reason"] = df.apply(reason, axis=1)
    df["exposure_usd"] = df["payment_value"].where(df["is_risk_flag"], 0).round(2)

    return df


def main():
    orders = load_orders()
    reviews = load_reviews()
    payments = load_payment_value()

    result = flag_orders(orders, reviews, payments)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "flagged_orders.csv"
    result.to_csv(out_path, index=False)

    total_orders = len(result)
    flagged = result["is_risk_flag"].sum()
    total_exposure = result["exposure_usd"].sum()

    print(f"Total orders: {total_orders:,}")
    print(f"Flagged as at-risk: {flagged:,} ({flagged / total_orders:.1%})")
    print(f"  - canceled/unavailable: {(result['risk_reason'] == 'canceled').sum():,}")
    print(f"  - low review (delivered): {(result['risk_reason'] == 'low_review').sum():,}")
    print(f"Total exposure from flagged orders: ${total_exposure:,.2f}")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
