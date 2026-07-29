# ISM Supply Chain Portfolio

A collection of supply chain analytics projects built to demonstrate the analytical skillset for Senior In-Stock Manager (ISM) roles — vendor risk management, inventory replenishment, and order/fraud risk exposure. All projects use Python (pandas) for data processing and Tableau for interactive dashboards, built on the [Olist Brazilian E-Commerce public dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Projects

### [Vendor Lead-Time (VLT) Risk Engine](./vlt-risk-engine)
Models vendor lead-time variability and translates it into dollar-denominated stockout exposure. Calculates dynamic safety stock and reorder points per vendor, segments vendors into risk tiers, and visualizes results in an Executive Overview dashboard focused on the highest-risk vendor segment.

**Key result:** 671 vendors flagged High Risk, $19,853.25 in stockout exposure, 81.7% overall service level for that segment.

### [Order Risk & Fraud Exposure Analysis](./fraud-exposure-analysis)
Identifies orders, sellers, and product categories with elevated fraud/cancellation risk using two proxy signals (canceled orders and low-review delivered orders), and quantifies the financial exposure they represent at both the seller and category level.

**Key result:** 13,545 orders flagged at-risk (13.6%), $2.58M in order-level exposure, with seller- and category-level risk segmentation.

## Tools Used Across Projects

Python (pandas), Tableau, Excel, SQL

## About

Each project folder contains its own README with full methodology, pipeline details, and dashboard screenshots.
