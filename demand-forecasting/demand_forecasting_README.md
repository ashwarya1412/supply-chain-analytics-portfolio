# Demand Forecasting & Inventory Overview

A supply chain analytics project examining demand trends, seasonality, and unmet demand across product categories — built with SQL as the primary analytical engine and Power BI for visualization, to demonstrate a broader tool set (beyond Python/Tableau) for a Senior In-Stock Manager (ISM) role.

## The Problem

Understanding *how much* demand a category generates is only half the picture — the more actionable question is *how well that demand is being met*, and *whether demand follows a predictable seasonal pattern* that inventory planning should account for. A category that looks fine on total volume alone can still be chronically understocked, and a demand spike that looks like an anomaly might actually be a recurring seasonal pattern.

## What This Project Does

Using the [Retail Store Inventory and Demand Forecasting dataset](https://www.kaggle.com/datasets/atomicd/retail-store-inventory-and-demand-forecasting) (daily store/product-level data with demand, units sold, inventory level, price, and promotion fields), this project:

1. Loads the raw daily data into a SQLite database (via DB Browser for SQLite)
2. Uses SQL to aggregate daily records into monthly demand by category
3. Computes **unmet demand** (the gap between total demand and units actually sold) at the category level
4. Builds a **3-month moving average** using a SQL window function, as a simple baseline trend signal against actual monthly demand
5. Visualizes results in an interactive **Power BI dashboard**

## Key Results

| Metric | Value |
|---|---|
| Categories | 5 |
| Total Demand | 8M units |
| Total Units Sold | 7M units |
| Overall Unmet Demand % | 14.85% |

**Unmet Demand % by Category:** Clothing highest at 15.96%, followed by Toys (15.29%), Groceries (14.96%), Electronics (14.81%), and Furniture lowest at 12.51%. Note: Groceries has the largest *absolute* unmet demand (550,349 units) despite a mid-pack percentage, since it has by far the highest total demand of any category — worth reading both the rate and the absolute volume together rather than either alone.

**Seasonality:** the monthly demand trend shows a clear recurring pattern — a mid-year dip and a spike around the December-January period across the 2-year history in the dataset, visible consistently when comparing actual demand against the 3-month moving average.

## Dashboard

The Power BI Demand Forecasting & Inventory Overview combines:
- **KPI strip** — Categories, Total Demand, Total Units Sold, Overall Unmet Demand %
- **Actual Demand vs. 3-Month Moving Average** — monthly trend line, filterable by category via a slicer
- **Unmet Demand % by Category** — bar chart ranking categories by how much demand goes unmet

See `/dashboard` for the Power BI file (`.pbix`) and a static screenshot.

## Project Structure

```
demand-forecasting/
├── data/raw/          # sales_data.csv (Kaggle: Retail Store Inventory and Demand Forecasting)
├── sql/
│   └── queries.sql            # Documented SQL views: monthly_category_demand,
│                               # category_demand_summary, monthly_demand_trend
├── outputs/
│   ├── monthly_category_demand.csv
│   ├── category_demand_summary.csv
│   └── monthly_demand_trend.csv
├── dashboard/
│   ├── demand_forecasting_overview.pbix
│   └── executive_overview_screenshot.png
└── README.md
```

## Key SQL Queries

**Monthly demand by category** (base aggregation feeding the trend chart):
```sql
SELECT 
    strftime('%Y-%m', "Date") AS year_month,
    "Category",
    SUM("Units Sold") AS total_units_sold,
    SUM("Demand") AS total_demand,
    AVG("Price") AS avg_price,
    AVG("Inventory Level") AS avg_inventory_level,
    SUM("Units Ordered") AS total_units_ordered,
    SUM(CASE WHEN "Promotion" = 1 THEN 1 ELSE 0 END) AS promo_days
FROM sales_data
GROUP BY year_month, "Category"
ORDER BY year_month, "Category";
```

**Category-level unmet demand summary:**
```sql
SELECT
    "Category",
    SUM("Units Sold") AS total_units_sold,
    SUM("Demand") AS total_demand,
    SUM("Demand") - SUM("Units Sold") AS unmet_demand,
    ROUND((SUM("Demand") - SUM("Units Sold")) * 100.0 / SUM("Demand"), 2) AS unmet_demand_pct,
    ROUND(AVG("Inventory Level"), 1) AS avg_inventory_level,
    ROUND(AVG("Price"), 2) AS avg_price,
    SUM("Units Ordered") AS total_units_ordered,
    SUM(CASE WHEN "Promotion" = 1 THEN 1 ELSE 0 END) AS promo_days,
    COUNT(*) AS record_count
FROM sales_data
GROUP BY "Category"
ORDER BY unmet_demand_pct DESC;
```

**3-month moving average (window function):**
```sql
CREATE VIEW monthly_demand_trend AS
SELECT
    year_month,
    "Category",
    total_units_sold,
    total_demand,
    ROUND(
        AVG(total_demand) OVER (
            PARTITION BY "Category"
            ORDER BY year_month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 1
    ) AS moving_avg_3mo,
    avg_price,
    avg_inventory_level,
    promo_days
FROM monthly_category_demand
ORDER BY "Category", year_month;
```

## How to Reproduce

1. Load `data/raw/sales_data.csv` into a SQLite database (DB Browser for SQLite: File → Import → Table from CSV)
2. Run the queries in `sql/queries.sql` in order — each is documented with its purpose and output
3. Export each view as CSV into `outputs/`
4. Open `dashboard/demand_forecasting_overview.pbix` in Power BI Desktop, or connect a new Power BI report to the three output CSVs

> **Note:** the `.db` file is a SQLite database and won't render as readable text in GitHub's file viewer. See `sql/queries.sql` or the queries above for the documented, human-readable version, or download the `.db` file and open it in [DB Browser for SQLite](https://sqlitebrowser.org/) to explore it directly.

## Methodology Notes

- **Unmet demand**: Demand − Units Sold, at the category level. This reflects the dataset's own `Demand` field compared against actual `Units Sold` — a proxy for stockout/fulfillment shortfall, not a directly labeled metric
- **3-month moving average**: computed with a SQL window function (`AVG() OVER (PARTITION BY Category ORDER BY year_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`), a simple baseline trend signal. The first two months per category have a partial-window average (fewer than 3 months of history), which is expected
- **Time range**: 25 months of data (Jan 2022 – Jan 2024) across 5 categories, 76,001 raw daily records

## Tools

SQL (SQLite via DB Browser for SQLite), Power BI

## Related Projects

- [`vlt-risk-engine`](../vlt-risk-engine) — vendor lead-time risk and inventory stockout exposure
- [`fraud-exposure-analysis`](../fraud-exposure-analysis) — order-level fraud/cancellation risk and financial exposure
- [`price-impact-analysis`](../price-impact-analysis) — pricing and competitive positioning analysis
