SELECT outlet,payment_method,loyalty,COUNT(*) orders,SUM(net_sales) revenue,AVG(net_sales) aov FROM orders GROUP BY 1,2,3;
