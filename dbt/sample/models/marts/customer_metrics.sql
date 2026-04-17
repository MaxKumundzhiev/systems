-- models/marts/customer_metrics.sql

{{ config(materialized='table') }}

WITH customer_orders AS (
    SELECT
        c.customer_id,
        c.name,
        c.email,
        c.signup_date,
        COUNT(o.order_id) as total_orders,
        SUM(o.amount) as total_spent,
        AVG(o.amount) as avg_order_value,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date
    FROM {{ ref('stg_customers') }} c
    LEFT JOIN {{ ref('stg_orders') }} o
        ON c.customer_id = o.customer_id
    GROUP BY 1, 2, 3, 4
)

SELECT
    *,
    (last_order_date - first_order_date) as customer_lifetime_days,
    CASE
        WHEN total_orders = 0 THEN 'No Orders'
        WHEN total_orders = 1 THEN 'One-time'
        WHEN total_orders <= 3 THEN 'Occasional'
        ELSE 'Frequent'
    END as customer_segment
FROM customer_orders