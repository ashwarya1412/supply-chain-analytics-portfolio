#  Supply Chain Analytics Portfolio

A collection of supply chain analytics projects covering vendor risk management, inventory replenishment, order/fraud risk exposure, and pricing analysis. All projects use Python (pandas) for data processing and Tableau for interactive dashboards.

## Projects

### [Vendor Lead-Time (VLT) Risk Engine](./vlt-risk-engine)
Models vendor lead-time variability and translates it into dollar-denominated stockout exposure. Calculates dynamic safety stock and reorder points per vendor, segments vendors into risk tiers, and visualizes results in an Executive Overview dashboard focused on the highest-risk vendor segment.

**Key result:** 671 vendors flagged High Risk, $19,853.25 in stockout exposure, 81.7% overall service level for that segment.

### [Order Risk & Fraud Exposure Analysis](./fraud-exposure-analysis)
Identifies orders, sellers, and product categories with elevated fraud/cancellation risk using two proxy signals (canceled orders and low-review delivered orders), and quantifies the financial exposure they represent at both the seller and category level.

**Key result:** 13,545 orders flagged at-risk (13.6%), $2.58M in order-level exposure, with seller- and category-level risk segmentation.

### [Price & Competitive Positioning Analysis](./price-impact-analysis)
Examines how pricing decisions relate to demand and competitive positioning, using a retail pricing dataset with competitor price/freight benchmarks. Computes price position relative to competitors and a price-volume correlation per category to identify which categories behave like classic price-sensitive demand — and which don't.

**Key result:** $961,751 in total revenue analyzed across 9 categories and 52 products; most categories show expected negative price-volume correlation, with `bed_bath_table` standing out as a counter-intuitive positive correlation (+0.371) worth further investigation.

## Tools Used Across Projects

Python (pandas), Tableau, Excel, SQL

## About

Each project folder contains its own README with full methodology, pipeline details, and dashboard screenshots.
