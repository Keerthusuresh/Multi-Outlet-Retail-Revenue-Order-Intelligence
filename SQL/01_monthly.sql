WITH monthly AS (
 SELECT strftime('%Y-%m',date) month, SUM(net_sales) revenue, COUNT(*) orders, AVG(net_sales) aov
 FROM orders GROUP BY 1
), lagged AS (
 SELECT *, LAG(month) OVER(ORDER BY month) prior_month, LAG(revenue) OVER(ORDER BY month) prior_revenue,
 LAG(orders) OVER(ORDER BY month) prior_orders,LAG(aov) OVER(ORDER BY month) prior_aov FROM monthly
)
SELECT *, CASE WHEN prior_month=strftime('%Y-%m',date(month||'-01','-1 month')) THEN 100.0*(revenue-prior_revenue)/NULLIF(prior_revenue,0) END mom_pct,
CASE WHEN prior_month=strftime('%Y-%m',date(month||'-01','-1 month')) THEN (orders-prior_orders)*prior_aov END volume_effect,
CASE WHEN prior_month=strftime('%Y-%m',date(month||'-01','-1 month')) THEN orders*(aov-prior_aov) END aov_effect FROM lagged;
