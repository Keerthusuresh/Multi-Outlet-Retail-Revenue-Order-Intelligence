WITH m AS (SELECT substr(date,1,7) month,outlet,SUM(net_sales) revenue,COUNT(*) orders,AVG(net_sales) aov FROM orders GROUP BY 1,2)
SELECT *,DENSE_RANK() OVER(PARTITION BY month ORDER BY revenue DESC) revenue_rank,100.0*revenue/NULLIF(SUM(revenue) OVER(PARTITION BY month),0) revenue_share_pct FROM m ORDER BY month,revenue_rank;
