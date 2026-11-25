SELECT outlet, strftime('%w',date) weekday_sunday_zero,hour,COUNT(*) orders,SUM(net_sales) revenue,AVG(net_sales) aov FROM orders GROUP BY 1,2,3 ORDER BY 1,2,3;
