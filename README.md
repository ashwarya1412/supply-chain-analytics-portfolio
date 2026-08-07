# Supply Chain Analytics Portfolio

A collection of supply chain analytics projects covering vendor risk management, inventory replenishment, order/fraud risk exposure, pricing analysis, demand forecasting, and warehouse management. Projects use Python (pandas), SQL, Tableau, Power BI, and Streamlit.

## Projects

### [Vendor Lead-Time (VLT) Risk Engine](https://github.com/ashwarya1412/supply-chain-analytics-portfolio/blob/main/vlt-risk-engine)
Models vendor lead-time variability and translates it into dollar-denominated stockout exposure. Calculates dynamic safety stock and reorder points per vendor, segments vendors into risk tiers, and visualizes results in an Executive Overview dashboard focused on the highest-risk vendor segment.

**Key result:** 671 vendors flagged High Risk, $19,853.25 in stockout exposure, 81.7% overall service level for that segment.

### [Order Risk & Fraud Exposure Analysis](https://github.com/ashwarya1412/supply-chain-analytics-portfolio/blob/main/fraud-exposure-analysis)
Identifies orders, sellers, and product categories with elevated fraud/cancellation risk using two proxy signals (canceled orders and low-review delivered orders), and quantifies the financial exposure they represent at both the seller and category level.

**Key result:** 13,545 orders flagged at-risk (13.6%), $2.58M in order-level exposure, with seller- and category-level risk segmentation.

### [Price & Competitive Positioning Analysis](https://github.com/ashwarya1412/supply-chain-analytics-portfolio/blob/main/price-impact-analysis)
Examines how pricing decisions relate to demand and competitive positioning, using a retail pricing dataset with competitor price/freight benchmarks. Computes price position relative to competitors and a price-volume correlation per category to identify which categories behave like classic price-sensitive demand — and which don't.

**Key result:** $961,751 in total revenue analyzed across 9 categories and 52 products; most categories show expected negative price-volume correlation, with `bed_bath_table` standing out as a counter-intuitive positive correlation (+0.371) worth further investigation.

### [Demand Forecasting & Inventory Overview](https://github.com/ashwarya1412/supply-chain-analytics-portfolio/blob/main/demand-forecasting)
Uses SQL as the primary analytical engine (window functions for a 3-month moving average) to examine demand trends, seasonality, and unmet demand across product categories, visualized in Power BI.

**Key result:** 8M units of total demand vs. 7M units sold (14.85% overall unmet demand) across 5 categories; identified a recurring seasonal pattern with demand peaking around December–January.

### [Operational Warehouse Management System (WMS) Engine](https://github.com/ashwarya1412/supply-chain-analytics-portfolio/blob/main/wms)
**🔗 [Live Demo](https://supply-chain-analytics-portfolio-kd588dqnknmv42kpzvwqyv.streamlit.app/)**

A full-stack, interactive WMS built with SQL, Python, and Streamlit. Features a 5-tier warehouse location hierarchy, serpentine pick-path routing to minimize picker travel distance, a dynamic replenishment engine flagging safety stock breaches, and ABC velocity/Pareto analysis for inventory slotting.

## Tools Used Across Projects

Python (pandas), SQL (SQLite), Tableau, Power BI, Streamlit, Excel

## About

Each project folder contains its own README with full methodology, pipeline details, and dashboard screenshots.