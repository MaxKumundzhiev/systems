{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    order_date::date as order_date,
    amount,
    status
FROM {{ ref('raw_orders') }}
WHERE status = 'completed'  -- только завершенные заказы