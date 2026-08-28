WITH daily AS (
    SELECT 
        order_date,
        COUNT(*) AS total_orders,
        SUM(order_amount) AS total_revenue,
        AVG(order_amount) AS avg_order_value
    FROM {{ ref('fact_orders') }}
    GROUP BY order_date
)

SELECT 
    order_date,
    total_orders,
    total_revenue,
    avg_order_value,
    total_revenue / NULLIF(total_orders, 0) AS revenue_per_order
FROM daily
ORDER BY order_date DESC
