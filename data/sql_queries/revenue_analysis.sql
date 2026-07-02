-- Monthly revenue analysis query

select
    date_trunc('month', order_created_at) as revenue_month,
    sum(gross_revenue) as gross_revenue,
    sum(discount_amount) as total_discounts,
    sum(refund_amount) as total_refunds,
    sum(net_revenue) as net_revenue
from analytics.fct_orders
where order_status = 'completed'
group by 1
order by 1;
