{{ config(materialized='table') }}

with orders as (
    select
        order_id,
        customer_id,
        order_status,
        order_created_at,
        gross_revenue,
        discount_amount,
        refund_amount,
        payment_status
    from {{ ref('stg_orders') }}
),

final as (
    select
        order_id,
        customer_id,
        order_status,
        order_created_at,
        gross_revenue,
        discount_amount,
        refund_amount,
        gross_revenue - discount_amount - refund_amount as net_revenue,
        payment_status
    from orders
    where payment_status = 'paid'
)

select * from final;
