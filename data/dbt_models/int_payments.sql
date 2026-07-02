{{ config(materialized='view') }}

select
    payment_id,
    order_id,
    payment_method,
    payment_status,
    payment_amount,
    payment_created_at
from {{ source('stripe', 'payments') }}
where payment_status in ('paid', 'refunded', 'failed');
