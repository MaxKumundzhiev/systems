{{ config(materialized='view') }}

SELECT 
    customer_id,
    name,
    email,
    signup_date::date as signup_date
FROM {{ ref('raw_customers') }}