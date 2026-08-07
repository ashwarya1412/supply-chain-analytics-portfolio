- ============================================================
-- 1. DATABASE SCHEMA SETUP (DDL)
-- ============================================================

-- Location Master (Zone -> Aisle -> Rack -> Shelf -> Bin)
CREATE TABLE IF NOT EXISTS warehouse_locations (
    location_id TEXT PRIMARY KEY,
    zone TEXT NOT NULL,
    aisle TEXT NOT NULL,
    rack TEXT NOT NULL,
    shelf TEXT NOT NULL,
    bin TEXT NOT NULL,
    is_active INTEGER DEFAULT 1
);

-- Master Product Catalog
CREATE TABLE IF NOT EXISTS product_catalog (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_weight_g REAL,
    product_length_cm REAL,
    product_height_cm REAL,
    product_width_cm REAL,
    reorder_point INTEGER DEFAULT 50,
    safety_stock INTEGER DEFAULT 20,
    max_stock INTEGER DEFAULT 500
);

-- Inventory Levels per Bin Location
CREATE TABLE IF NOT EXISTS inventory_levels (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    location_id TEXT,
    qty_on_hand INTEGER DEFAULT 0 CHECK (qty_on_hand >= 0),
    qty_allocated INTEGER DEFAULT 0 CHECK (qty_allocated >= 0),
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES product_catalog(product_id),
    FOREIGN KEY(location_id) REFERENCES warehouse_locations(location_id),
    UNIQUE(product_id, location_id)
);

-- Audit Transaction Log
CREATE TABLE IF NOT EXISTS inventory_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT,
    from_location_id TEXT,
    to_location_id TEXT,
    qty_changed INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- 'RECEIVING', 'PICK', 'TRANSFER', 'CYCLE_COUNT'
    transaction_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. SEED WAREHOUSE LOCATION HIERARCHY (100 BINS)
-- ============================================================
WITH RECURSIVE 
    zones(z) AS (VALUES ('A'), ('B'), ('C'), ('D')),
    aisles(a) AS (SELECT 1 UNION ALL SELECT a + 1 FROM aisles WHERE a < 5),
    racks(r) AS (SELECT 1 UNION ALL SELECT r + 1 FROM racks WHERE r < 5)
INSERT OR IGNORE INTO warehouse_locations (location_id, zone, aisle, rack, shelf, bin, is_active)
SELECT 
    'WH1-Z' || z || '-A0' || a || '-R0' || r || '-B01' AS location_id,
    'Zone-' || z AS zone,
    'Aisle-0' || a AS aisle,
    'Rack-0' || r AS rack,
    'Shelf-01' AS shelf,
    'Bin-01' AS bin,
    1 AS is_active
FROM zones, aisles, racks;


-- ============================================================
-- 3. SEED INVENTORY BALANCES FOR ALL SKUs
-- ============================================================
INSERT OR IGNORE INTO inventory_levels (product_id, location_id, qty_on_hand, qty_allocated, last_updated)
SELECT 
    p.product_id,
    w.location_id,
    (abs(random()) % 250) + 10 AS qty_on_hand,
    (abs(random()) % 8) AS qty_allocated,
    CURRENT_TIMESTAMP
FROM product_catalog p
JOIN (
    SELECT location_id, ROW_NUMBER() OVER (ORDER BY location_id) AS row_num 
    FROM warehouse_locations
) w ON (abs(random()) % 100 + 1) = w.row_num;