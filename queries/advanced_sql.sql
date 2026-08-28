-- ============================================
-- 1. QUERY OPTIMIZATION WITH EXPLAIN ANALYZE
-- ============================================

-- Before optimization
EXPLAIN ANALYZE
SELECT region, COUNT(*) as orders, SUM(order_amount) as revenue
FROM fact_orders
WHERE order_status = 'completed'
GROUP BY region;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_order_status ON fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_order_date ON fact_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_region ON fact_orders(region);

-- After optimization
EXPLAIN ANALYZE
SELECT region, COUNT(*) as orders, SUM(order_amount) as revenue
FROM fact_orders
WHERE order_status = 'completed'
GROUP BY region;

-- ============================================
-- 2. WINDOW FUNCTIONS
-- ============================================

-- Running total by region
SELECT 
    order_date,
    region,
    order_amount,
    SUM(order_amount) OVER (PARTITION BY region ORDER BY order_date) as running_revenue
FROM fact_orders
WHERE order_status = 'completed'
ORDER BY region, order_date;

-- Rank products by revenue
SELECT 
    product_id,
    SUM(order_amount) as revenue,
    RANK() OVER (ORDER BY SUM(order_amount) DESC) as rank
FROM fact_orders
WHERE order_status = 'completed'
GROUP BY product_id;

-- ============================================
-- 3. CTE (Common Table Expressions)
-- ============================================

WITH daily_stats AS (
    SELECT DATE(order_date) as day, COUNT(*) as orders, SUM(order_amount) as revenue
    FROM fact_orders
    WHERE order_status = 'completed'
    GROUP BY DATE(order_date)
)
SELECT 
    day,
    orders,
    revenue,
    LAG(revenue) OVER (ORDER BY day) as prev_day,
    (revenue - LAG(revenue) OVER (ORDER BY day)) / LAG(revenue) OVER (ORDER BY day) * 100 as growth_pct
FROM daily_stats
ORDER BY day DESC;

-- ============================================
-- 4. COMPOSITE INDEX
-- ============================================

CREATE INDEX IF NOT EXISTS idx_order_status_region ON fact_orders(order_status, region);
CREATE INDEX IF NOT EXISTS idx_active_orders ON fact_orders(order_id) WHERE order_status IN ('pending', 'shipped');
