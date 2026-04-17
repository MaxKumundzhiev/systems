-- Проверить что все суммы заказов положительные
SELECT
    order_id,
    amount
FROM {{ ref('stg_orders') }}
WHERE amount <= 0