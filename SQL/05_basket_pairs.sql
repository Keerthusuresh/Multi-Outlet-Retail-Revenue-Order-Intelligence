WITH pairs AS (
 SELECT a.product_id product_a,b.product_id product_b,COUNT(*) pair_orders
 FROM basket_mentions a JOIN basket_mentions b ON a.receipt=b.receipt AND a.product_id<b.product_id GROUP BY 1,2
), counts AS (SELECT product_id,COUNT(*) orders FROM basket_mentions GROUP BY 1)
SELECT p.*, 1.0*pair_orders/NULLIF((SELECT COUNT(*) FROM orders),0) support_all_orders,
1.0*pair_orders/a.orders confidence_a_to_b,
1.0*pair_orders*(SELECT COUNT(DISTINCT receipt) FROM basket_mentions)/NULLIF(1.0*a.orders*b.orders,0) lift_matched_receipts
FROM pairs p JOIN counts a ON p.product_a=a.product_id JOIN counts b ON p.product_b=b.product_id ORDER BY pair_orders DESC;
