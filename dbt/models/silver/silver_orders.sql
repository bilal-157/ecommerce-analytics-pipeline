SELECT 
    order_id,
    customer_id,
    product_id,
    order_date,
    order_amount,
    order_status,
    region,
    CASE 
        WHEN order_status = 'completed' THEN 'completed'
        WHEN order_status IN ('pending', 'shipped') THEN 'in_progress'
        ELSE 'other'
    END AS status_category
FROM {{ ref('bronze_orders') }}
WHERE order_amount > 0
