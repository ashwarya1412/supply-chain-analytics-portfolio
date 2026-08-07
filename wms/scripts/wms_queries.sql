/*
================================================================================
CORE WMS OPERATIONAL LOGIC & REPORTING VIEWS
================================================================================
*/

-- ============================================================
-- 1. OPTIMIZED PICK PATH ROUTE (SERPENTINE PATH)
-- ============================================================
-- Minimizes picker foot movement by sorting picks sequentially by Zone -> Bin
SELECT 
    w.zone,
    w.aisle,
    w.rack,
    w.shelf,
    w.bin,
    i.location_id,
    i.product_id,
    p.product_category_name,
    i.qty_on_hand,
    i.qty_allocated,
    (i.qty_on_hand - i.qty_allocated) AS qty_available,
    MIN(5, (i.qty_on_hand - i.qty_allocated)) AS qty_to_pick, 
    'PICK_ORDER_9901' AS order_reference
FROM inventory_levels i
JOIN warehouse_locations w ON i.location_id = w.location_id
JOIN product_catalog p ON i.product_id = p.product_id
WHERE (i.qty_on_hand - i.qty_allocated) > 0
ORDER BY 
    w.zone ASC, 
    w.aisle ASC, 
    w.rack ASC, 
    w.shelf ASC, 
    w.bin ASC;


-- ============================================================
-- 2. AUTOMATED REPLENISHMENT & STOCKOUT RISK VIEW
-- ============================================================
CREATE VIEW IF NOT EXISTS v_wms_replenishment_alerts AS
SELECT 
    p.product_id,
    p.product_category_name,
    COALESCE(SUM(i.qty_on_hand), 0) AS total_on_hand,
    COALESCE(SUM(i.qty_allocated), 0) AS total_allocated,
    COALESCE(SUM(i.qty_on_hand - i.qty_allocated), 0) AS total_available,
    p.safety_stock,
    p.reorder_point,
    p.max_stock,
    CASE 
        WHEN COALESCE(SUM(i.qty_on_hand - i.qty_allocated), 0) <= p.reorder_point 
            THEN (p.max_stock - COALESCE(SUM(i.qty_on_hand - i.qty_allocated), 0))
        ELSE 0
    END AS target_po_reorder_qty,
    CASE 
        WHEN COALESCE(SUM(i.qty_on_hand - i.qty_allocated), 0) <= p.safety_stock 
            THEN 'CRITICAL: Safety Stock Breached'
        WHEN COALESCE(SUM(i.qty_on_hand - i.qty_allocated), 0) <= p.reorder_point 
            THEN 'WARNING: Reorder Point Hit'
        ELSE 'HEALTHY'
    END AS inventory_health_status
FROM product_catalog p
LEFT JOIN inventory_levels i ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_category_name, p.safety_stock, p.reorder_point, p.max_stock;


-- ============================================================
-- 3. ABC PARETO VELOCITY CLASSIFICATION VIEW
-- ============================================================
CREATE VIEW IF NOT EXISTS v_wms_abc_pareto_analysis AS
WITH sku_valuations AS (
    SELECT 
        p.product_id,
        p.product_category_name,
        SUM(i.qty_on_hand) AS total_units,
        COALESCE(p.product_weight_g, 100) AS unit_weight_g,
        SUM(i.qty_on_hand) * COALESCE(p.product_weight_g, 100) AS total_weight_volume
    FROM product_catalog p
    JOIN inventory_levels i ON p.product_id = i.product_id
    GROUP BY p.product_id, p.product_category_name
),
cumulative_ranks AS (
    SELECT 
        product_id,
        product_category_name,
        total_units,
        total_weight_volume,
        CUME_DIST() OVER (ORDER BY total_units DESC) AS cumulative_pct
    FROM sku_valuations
)
SELECT 
    product_id,
    product_category_name,
    total_units,
    total_weight_volume,
    ROUND(cumulative_pct * 100, 2) AS percentile_rank,
    CASE 
        WHEN cumulative_pct <= 0.20 THEN 'Class A (Fast Mover)'
        WHEN cumulative_pct <= 0.50 THEN 'Class B (Medium Mover)'
        ELSE 'Class C (Slow Mover)'
    END AS abc_velocity_class
FROM cumulative_ranks;