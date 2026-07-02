{{ config(materialized='table') }}

with customers as (
    select
        customer_id,
        first_order_date,
        last_order_date,
        total_orders,
        total_net_revenue
    from {{ ref('int_customer_orders') }}
),

final as (
    select
        customer_id,
        first_order_date,
        last_order_date,
        total_orders,
        total_net_revenue,
        total_net_revenue / nullif(total_orders, 0) as avg_order_value,
        case
            when total_orders >= 10 then 'high_value'
            when total_orders >= 3 then 'medium_value'
            else 'low_value'
        end as customer_segment
    from customers
)

select * from final;
