# Price & Competitive Positioning Analysis

A supply chain analytics project examining how pricing decisions relate to demand and competitive positioning — built to demonstrate the analytical skillset of a Senior In-Stock Manager (ISM) role.

## The Problem

Pricing decisions don't happen in a vacuum — they interact with competitor pricing, freight costs, and demand in ways that aren't always intuitive. A category-wide "raise prices to improve margin" strategy can backfire in price-sensitive categories, while it may have little effect in others. Understanding which categories behave like classic price-sensitive demand — and which don't — is essential before making pricing or promotion decisions.

## What This Project Does

Using the [Retail Price Optimization dataset](https://www.kaggle.com/datasets/suddharshan/retail-price-optimization) (Olist-based, with monthly product-level pricing, competitor pricing, and freight data), this project:

1. Computes each product's price position relative to competitors (Above / At / Below Market), using average of three competitor price points per record
2. Computes freight cost position relative to competitor freight pricing
3. Calculates a price-volume correlation per category — a descriptive signal for how demand responds to price within that category
4. Rolls results up to both **category-level** and **product-level** summaries
5. Visualizes results in an interactive **Tableau Price & Competitive Positioning Overview** dashboard

## Key Results

| Metric | Value |
|---|---|
| Total Revenue | $961,751.10 |
| Categories | 9 |
| Products | 52 |
| Avg Price vs. Competitor (category-average basis) | $11.58 |

**Price Position:** 279 records Above Market, 202 At Market, 195 Below Market (±$5 tolerance band)

**Price-Volume Correlation by Category** — most categories show the expected negative relationship (higher price, lower demand), led by `consoles_games` (-0.566). Three categories buck the trend with a positive correlation, most notably `bed_bath_table` (+0.371) — flagged as a standout finding worth further investigation rather than a definitive causal claim, given the descriptive (not experimental) nature of this analysis.

## Dashboard

The Tableau Price & Competitive Positioning Overview combines:
- **KPI strip** — Total Revenue, Products, Categories, Avg Price vs. Competitor
- **Price-Volume Correlation by Category** — the centerpiece chart, showing which categories behave like textbook price-sensitive demand and which don't
- **Price Position by Category** — Above/At/Below Market record counts per category
- **Top 10 Products by Revenue**

See `/dashboard` for the packaged Tableau workbook (`.twbx`) and a static screenshot.

## Project Structure

```
price-impact-analysis/
├── data/raw/          # retail_price.csv (Kaggle: Retail Price Optimization)
├── scripts/
│   ├── price_metrics.py            # Row-level derived metrics (competitor position, freight position)
│   └── category_price_summary.py   # Rolls up to category-level and product-level summaries
├── outputs/
│   ├── price_metrics_enriched.csv
│   ├── category_price_summary.csv
│   └── product_price_summary.csv
├── dashboard/
│   ├── price_impact_analysis.twbx
│   └── executive_overview_screenshot.png
└── README.md
```

## How to Reproduce

```bash
# 1. Install dependencies
pip install pandas

# 2. Run the pipeline in order
python scripts/price_metrics.py
python scripts/category_price_summary.py

# 3. Open outputs/category_price_summary.csv and product_price_summary.csv in Tableau
```

## Methodology Notes

- **Price position tolerance**: records within ±$5 of the average competitor price are classified "At Market"; outside that band, "Above" or "Below Market"
- **Price-volume correlation**: a simple Pearson correlation between unit price and quantity sold, computed per category (minimum 5 records with price variation required — otherwise reported as not available). This is a descriptive signal, not a causal estimate; the dataset is monthly product-level data (676 records across 9 categories), so correlations should be read as directional signals to investigate further, not definitive elasticity figures
- **Revenue**: uses the dataset's `total_price` field directly (already qty × unit_price)

## Tools

Python (pandas), Tableau

## Related Projects

- [`vlt-risk-engine`](../vlt-risk-engine) — vendor lead-time risk and inventory stockout exposure
- [`fraud-exposure-analysis`](../fraud-exposure-analysis) — order-level fraud/cancellation risk and financial exposure
