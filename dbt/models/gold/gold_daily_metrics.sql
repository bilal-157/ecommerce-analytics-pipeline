SELECT 
    DATE(order_date) AS day,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(order_amount) AS total_revenue,
    AVG(order_amount) AS avg_order_value
FROM {{ ref('silver_orders') }}
WHERE order_status = 'completed'
GROUP BY DATE(order_date), region
