# Power BI Desktop implementation

Status: specification and DAX supplied; not executed in Power BI Desktop. No PBIX is included. Run Python first with the original CSVs. Do not use the synthetic unit test as real data.

1. Open Power BI Desktop on Windows. Get Data > Text/CSV, import output/FactOrders.csv, DimDate.csv, DimOutlet.csv, DimProduct.csv, BasketMentions.csv. Use Transform Data. Rename queries to match filenames without extensions.
2. In Power Query, set receipt, outlet, product_id, items, payment_method, loyalty and month to Text; date to Date (ISO yyyy-MM-dd); hour, weekday_number and item_count to Whole Number; net_sales, tax, total_amount and catalog_price to Decimal Number. Use English (United States) locale for the generated decimal CSV values. Verify zero conversion errors. Close & Apply.
3. Model view: DimDate[date] 1 -> * FactOrders[date]; DimOutlet[outlet] 1 -> * FactOrders[outlet]; FactOrders[receipt] 1 -> * BasketMentions[receipt]; DimProduct[product_id] 1 -> * BasketMentions[product_id]. Single filter direction, from one to many. Mark DimDate as date table. Sort weekday by weekday_number. Do not create a bidirectional relationship: receipt-level revenue must not be attributed to products without line-item values.
4. Modeling > New measure, paste each individual expression from measures.dax. Set monetary measures to IDR, percentages to percentage, counts to integers. MoM measures should be used in complete calendar-month context, not an arbitrary partial date selection. Check first month returns blank.
5. Import theme.json through View > Themes > Browse for themes. Set page size 16:9. Use a consistent white background, dark navy text, teal for primary values and orange for exceptions.

## Page 1: Executive performance
- Cards: Net Revenue, Orders, Average Order Value, MoM Revenue %, Tax Collected.
- Line chart: DimDate[month] / Net Revenue. Clustered columns: month / Orders. Matrix: outlet, Net Revenue, Orders, AOV, Outlet Rank.
- Slicers: month, outlet. Tooltips: Orders, AOV, Net Revenue.
- Add a second monthly chart for Volume Effect and AOV Effect. Their sum must reconcile to the revenue difference.

## Page 2: Outlet and operations
- Bar chart: outlet / Net Revenue; matrix: weekday, hour / Orders with conditional background formatting. Payment method chart: Orders by payment_method. Loyalty usage chart: Orders by loyalty (not unique or repeat customers).
- Slicers: month and outlet. Add an outlet detail drill-through page or drill-through field on this page; test navigation from Page 1.
- Interpret peak hours as demand indicators, not proof of understaffing. No costs or labor hours are provided.

## Page 3: Product and basket intelligence
- Only publish after inspecting unmatched_items.csv and validating the Items delimiters against source records. Display match coverage prominently.
- Bar: product_name / Product Basket Count. Matrix: category, product_name, Product Basket Count, Basket Penetration. Slicers: month, outlet, category.
- Count distinct receipts mentioning products; categories overlap. Do not display product revenue, product units sold, profitability or repeat customer rate from these data.
- Use output/05_basket_pairs.csv as an optional static association table; label scope as full dataset (not filtered by outlet/month). Only discuss pairs after coverage validation.

## Acceptance checks
- Compare total revenue and order count with output/validation.json. Compare monthly and outlet totals with 01_monthly.csv and 02_outlets.csv. Compare DAX volume+AOV effects to monthly revenue differences.
- Test each slicer, cross-filter, drill-through, and reset. Confirm product visuals never inflate receipt revenue.
- Save as Retail_Intelligence.pbix. Export screenshots/PDF of the three pages; add to GitHub after review. A public Power BI Service link requires appropriate account and tenant permissions; do not enable public sharing without checking data policy.
