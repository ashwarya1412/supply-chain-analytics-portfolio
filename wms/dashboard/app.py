import streamlit as st
import sqlite3
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="WMS Portfolio Engine", layout="wide")

# Determine relative path to the database file in data/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "..", "data", "wms_portfolio.db")

# Fallback if launched directly from project root
if not os.path.exists(DB_FILE):
    DB_FILE = os.path.join("data", "wms_portfolio.db")

def run_query(query):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# App Header
st.title("📦 Operational Warehouse Management System (WMS)")
st.markdown("---")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Module:", 
    ["Overview", "Pick Path Routing", "Replenishment Alerts", "ABC Pareto Analysis"]
)

# -------------------------------------------------------------------
# MODULE 1: OVERVIEW
# -------------------------------------------------------------------
if page == "Overview":
    st.subheader("📊 Warehouse Key Performance Indicators")
    
    try:
        total_skus = run_query("SELECT COUNT(*) as count FROM product_catalog")['count'][0]
        total_on_hand = run_query("SELECT SUM(qty_on_hand) as total FROM inventory_levels")['total'][0]
        critical = run_query("SELECT COUNT(*) as count FROM v_wms_replenishment_alerts WHERE inventory_health_status LIKE 'CRITICAL%'")['count'][0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Catalog SKUs", f"{total_skus:,}")
        col2.metric("Total Units On-Hand", f"{int(total_on_hand or 0):,}")
        col3.metric("Critical Safety Stock Alerts", f"{critical:,}", delta="-Stock Risk", delta_color="inverse")
        
        st.markdown("---")
        st.subheader("Live Inventory Balances (Top 100 Bins)")
        sample_df = run_query("""
            SELECT i.product_id, p.product_category_name, i.location_id, w.zone, 
                   i.qty_on_hand, i.qty_allocated, (i.qty_on_hand - i.qty_allocated) as qty_available
            FROM inventory_levels i
            JOIN product_catalog p ON i.product_id = p.product_id
            JOIN warehouse_locations w ON i.location_id = w.location_id
            LIMIT 100
        """)
        st.dataframe(sample_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error connecting to database at {DB_FILE}. Make sure wms_portfolio.db is inside the data/ folder! Error details: {e}")

# -------------------------------------------------------------------
# MODULE 2: PICK PATH ROUTING
# -------------------------------------------------------------------
elif page == "Pick Path Routing":
    st.subheader("🗺️ Serpentine Pick Path Optimization")
    st.info("Pick paths are ordered by Zone -> Aisle -> Rack -> Shelf -> Bin to minimize travel distance.")
    
    query = """
        SELECT w.zone, w.aisle, w.rack, w.shelf, w.bin, i.location_id, i.product_id,
               p.product_category_name,
               (i.qty_on_hand - i.qty_allocated) AS qty_available,
               MIN(5, (i.qty_on_hand - i.qty_allocated)) AS qty_to_pick,
               'PICK_ORDER_9901' AS order_reference
        FROM inventory_levels i
        JOIN warehouse_locations w ON i.location_id = w.location_id
        JOIN product_catalog p ON i.product_id = p.product_id
        WHERE (i.qty_on_hand - i.qty_allocated) > 0
        ORDER BY w.zone ASC, w.aisle ASC, w.rack ASC, w.shelf ASC, w.bin ASC
        LIMIT 50
    """
    st.dataframe(run_query(query), use_container_width=True)

# -------------------------------------------------------------------
# MODULE 3: REPLENISHMENT ALERTS
# -------------------------------------------------------------------
elif page == "Replenishment Alerts":
    st.subheader("🚨 Purchase Order & Replenishment Triggers")
    alerts_df = run_query("SELECT * FROM v_wms_replenishment_alerts ORDER BY total_available ASC")
    st.dataframe(alerts_df, use_container_width=True)

# -------------------------------------------------------------------
# MODULE 4: ABC PARETO ANALYSIS
# -------------------------------------------------------------------
elif page == "ABC Pareto Analysis":
    st.subheader("📈 ABC Pareto Velocity Classification")
    st.markdown("Class A = High Velocity (Dock/Fast-pick), Class B = Medium, Class C = Slow Mover.")
    abc_df = run_query("SELECT * FROM v_wms_abc_pareto_analysis ORDER BY total_units DESC")
    st.dataframe(abc_df, use_container_width=True)