# E-Commerce Inventory Replenishment & Vendor Lead Time (VLT) Risk Engine

A supply chain analytics project that models vendor lead-time risk and translates it into dollar-denominated stockout exposure — built to demonstrate the analytical skillset of a Senior In-Stock Manager (ISM) role.

## The Problem

Not all vendor delays carry the same business cost. A vendor with an unpredictable lead time supplying a low-volume, low-margin product is a very different risk than one supplying a high-velocity, high-exposure SKU. Treating every late vendor the same wastes attention on low-stakes problems while high-exposure risks go unmanaged.

## What This Project Does

Using the [Olist Brazilian E-Commerce public dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), this project:

1. Calculates **Vendor Lead Time (VLT) variance** and on-time delivery rate per vendor
2. Computes **Dynamic Safety Stock** (Z = 1.65, targeting a 95% service level) and **Reorder Points (ROP)** per vendor
3. Estimates **stockout risk units** — demand during lead time not covered by safety stock
4. Converts that into **financial exposure ($)** using historical average selling price, plus an assumed gross margin for margin-at-risk
5. Segments vendors into **Risk Tiers** (High / Medium / Low) based on on-time rate and lead-time coefficient of variation
6. Visualizes results in an interactive **Tableau Executive Overview dashboard**

## Key Results (High Risk Segment)

| Metric | Value |
|---|---|
| Vendors Flagged High Risk | 671 |
| Total Stockout Exposure | $19,853.25 |
| Average Lead Time | 14.2 days |
| Overall Service Level | 81.7% |

## Dashboard

The Tableau Executive Overview combines:
- **Vendor Risk Quadrant** — delivery unpredictability (VLT coefficient of variation) vs. order volume, sized by exposure
- **Exposure by State** — geographic concentration of financial risk
- **Top 10 Vendors by Exposure** — a concrete, ranked action list
- **KPI strip** — Total Exposure, Vendor Count, Avg VLT, and Overall Service Level, scoped to the High Risk segment

See `/dashboard` for the packaged Tableau workbook (`.twbx`) and a static screenshot.

## Project Structure

```
vlt-risk-engine/
├── data/raw/          # Olist source CSVs
├── scripts/
│   ├── reorder_point.py    # Safety stock & reorder point calculations
│   └── exposure.py         # Financial exposure & risk tier calculations
├── outputs/
│   ├── reorder_point_by_vendor.csv
│   └── vendor_risk_summary.csv   # Final dataset feeding Excel/Tableau
├── dashboard/
│   ├── vlt_risk_engine.twbx
│   └── executive_overview_screenshot.png
├── README.md
└── .gitignore
```

## How to Reproduce

```bash
# 1. Install dependencies
pip install pandas

# 2. Run the pipeline in order
python scripts/reorder_point.py
python scripts/exposure.py

# 3. Open outputs/vendor_risk_summary.csv in Tableau or Excel
```

## Methodology Notes

- **Safety stock** uses a standard normal Z-score of 1.65, corresponding to a 95% service level target
- **Assumed gross margin** for margin-at-risk calculations is set at 30% (adjustable in `exposure.py`)
- **Risk Tier** thresholds: High Risk if on-time rate < 85% OR lead-time CV > 0.75; Medium Risk if on-time rate < 92% OR CV > 0.5; otherwise Low Risk

## Tools

Python (pandas), Tableau, Excel

## Author

Built as part of a supply chain analytics portfolio targeting Senior In-Stock Manager (ISM) roles at Amazon.
