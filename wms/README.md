# 📦 Operational Warehouse Management System (WMS) Engine


**🔗 Live Demo:** https://supply-chain-analytics-portfolio-kd588dqnknmv42kpzvwqyv.streamlit.app/

A full-stack, operational Warehouse Management System (WMS) built using SQL, Python, and Streamlit on real-world e-commerce data from Kaggle (Olist Dataset).

## 🚀 Key Supply Chain Features
1. **Warehouse Location Hierarchy:** 5-tier location model (`Zone` -> `Aisle` -> `Rack` -> `Shelf` -> `Bin`).
2. **Serpentine Pick Routing:** Optimizes fulfillment travel paths sequentially to minimize picker travel distance.
3. **Dynamic Replenishment Engine:** Automated SQL View flagging safety stock breaches ($Min/Max$) and recommending purchase order quantities.
4. **ABC Velocity Pareto Analysis:** Uses SQL window functions (`CUME_DIST()`) to classify inventory into Class A (Fast Movers), B (Medium), and C (Slow Stock) for optimized slotting.

## 🛠️ Tech Stack & Directory Structure
* **Database:** SQLite
* **Analytics/Backend:** Python (`pandas`, `sqlite3`)
* **Dashboard Interface:** Streamlit

```text
wms/
│
├── dashboard/
│   └── app.py             <-- Streamlit Web Application
├── data/
│   ├── olist_products_dataset.csv
│   └── wms_portfolio.db   <-- Relational Database
├── scripts/
│   ├── schema_and_seed.sql
│   └── wms_queries.sql
└── README.md