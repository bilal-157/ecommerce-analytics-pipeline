-- ============================================
-- 1. STAR SCHEMA - SCD TYPE 2 DIMENSION
-- ============================================

CREATE TABLE IF NOT EXISTS dim_customer_scd (
    customer_sk INTEGER PRIMARY KEY,
    customer_id INTEGER,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    region VARCHAR(20),
    customer_segment VARCHAR(20),
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- Sample SCD Type 2 data
INSERT INTO dim_customer_scd VALUES
    (1, 1, 'John Doe', 'john@email.com', 'North', 'Premium', '2024-01-01', '2024-06-30', FALSE),
    (2, 1, 'John Doe', 'john.doe@email.com', 'North', 'Premium', '2024-07-01', '9999-12-31', TRUE),
    (3, 2, 'Jane Smith', 'jane@email.com', 'South', 'Regular', '2024-01-01', '9999-12-31', TRUE);

-- ============================================
-- 2. SCD TYPE 2 QUERIES
-- ============================================

-- Get current customers
SELECT * FROM dim_customer_scd WHERE is_current = TRUE;

-- Get customer history
SELECT customer_id, customer_name, region, valid_from, valid_to
FROM dim_customer_scd
WHERE customer_id = 1
ORDER BY valid_from;

-- ============================================
-- 3. DIMENSION TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    unit_price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    day_of_week INTEGER
);

-- ============================================
-- 4. STAR SCHEMA ANALYTICS
-- ============================================

SELECT 
    c.region,
    c.customer_segment,
    COUNT(f.order_id) as total_orders,
    SUM(f.order_amount) as total_revenue,
    AVG(f.order_amount) as avg_order_value
FROM fact_orders f
LEFT JOIN dim_customer_scd c ON f.customer_id = c.customer_id AND c.is_current = TRUE
WHERE f.order_status = 'completed'
GROUP BY c.region, c.customer_segment
ORDER BY total_revenue DESC;
