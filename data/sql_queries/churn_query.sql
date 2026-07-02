-- Customers are considered churned if they have not ordered in the last 60 days.

select
    customer_id,
    last_order_date,
    current_date - last_order_date as days_since_last_order,
    case
        when current_date - last_order_date > 60 then 1
        else 0
    end as is_churned
from analytics.dim_customers;
