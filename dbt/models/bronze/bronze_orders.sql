-- dbt/models/bronze/bronze_orders.sql (raw data from API)
SELECT * FROM bronze_orders

-- dbt/models/silver/silver_orders.sql (cleaned data)
SELECT 
    order_id,
    product_id,
    product_name,
    price,
    category,
    quantity,
    (price * quantity) AS total_amount,
    order_status,
    ingested_at
FROM bronze_orders
WHERE price > 0 AND quantity > 0

-- dbt/models/gold/gold_daily_metrics.sql (analytics)
SELECT 
    DATE(ingested_at) AS order_date,
    category,
    COUNT(*) AS total_orders,
    SUM(price * quantity) AS total_revenue,
    AVG(price * quantity) AS avg_order_value
FROM silver_orders
GROUP BY DATE(ingested_at), category