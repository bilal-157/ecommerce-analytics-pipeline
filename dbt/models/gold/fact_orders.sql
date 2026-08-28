WITH orders AS (
    SELECT 
        order_id,
        customer_id,
        order_amount,
        order_status,
        timestamp::DATE AS order_date
    FROM {{ source('bronze', 'orders') }}
    WHERE order_status = 'completed'
)

SELECT 
    order_id,
    customer_id,
    order_amount,
    order_date,
    order_amount * 0.15 AS estimated_profit
FROM orders
