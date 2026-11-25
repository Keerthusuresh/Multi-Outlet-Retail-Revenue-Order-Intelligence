# Multi-Outlet Retail Revenue & Order Intelligence

**Business case:** A regional F&B manager needs to distinguish revenue changes driven by demand from changes in basket value, compare outlets, and identify potential cross-selling opportunities. This repository supplies a reproducible Python + SQLite analytics pipeline and a Power BI report implementation plan.

## Status
- Python/SQLite code implemented and tested on a small synthetic fixture only.
- Original data acquisition blocked in the authoring environment; full-data execution, measured findings and Power BI Desktop report build are pending.
- No PBIX, live deployment, commercial impact or verified real-data metrics are claimed.

## Source
Engel, M. M., Gaol, F. L., Kurniawan, A., & Budiharto, W. (2026). *Anonymous Transactional Dataset*, Mendeley Data V2. https://doi.org/10.17632/kcgf45y24m.2 (CC BY 4.0, per dataset page). Download: https://data.mendeley.com/datasets/kcgf45y24m/2 . Documentation: https://pmc.ncbi.nlm.nih.gov/articles/PMC12907624/ .
The accompanying paper reports 53,820 POS records, three outlets and 96 catalog products for January–September 2025, in Surabaya, Indonesia. These are publisher-reported figures, not results independently reproduced here. Revenue is net sales, excluding tax, in IDR. The dataset has no customer IDs. 

## Run locally
1. Install Python 3.10+ (SQLite included; no third-party dependencies).
2. Download the two V2 CSVs, `Transactions.csv` and `Products.csv`, from the source. Place them under `data/raw/` without editing the original files.
3. In the project folder run:
```sh
python -m unittest discover -s tests -v
python run.py
```
4. Inspect `output/validation.json`, `rejected.csv`, `quality_flags.csv` and `unmatched_items.csv`. If the schema or parsing fails, inspect original headers and delimiters; do not override checks blindly. A conflicting receipt ID stops processing. Exact duplicate rows are removed; invalid records are logged; nonpositive revenue is retained and flagged.
5. Follow [Power BI setup](powerbi/BUILD.md) to import the clean CSVs and implement measures and visuals. Save PBIX locally and add it after acceptance checks.

## Analytical outputs
| File | Purpose |
|---|---|
| 01_monthly.csv | Monthly revenue, orders, AOV, MoM growth and exact volume/AOV decomposition using CTEs and LAG |
| 02_outlets.csv | Monthly outlet benchmarks, DENSE_RANK and share |
| 03_hourly.csv | Weekday/hour demand by outlet |
| 04_payments.csv | Payment and loyalty usage by outlet |
| 05_basket_pairs.csv | Co-occurrence, support, confidence and lift (matched subset caveat) |
| validation.json | Source-to-output reconciliation and match coverage |
| FactOrders.csv, DimDate.csv, DimOutlet.csv | Receipt-level BI model |
| DimProduct.csv, BasketMentions.csv | Product mentions, separate from receipt amounts |

## Method and limitations
Receipt is the transaction grain as documented; unique keys are enforced. Sales are not duplicated across product mentions. Product matching is intentionally conservative and provisional: delimiters and names need verification against real CSVs. Association confidence is conditional on matched product mentions; unmatched baskets can bias results. No per-item sales, margin, refunds, staffing, repeat customer or actual loyalty retention metrics are inferred. No causal claims about promotions or staffing. The source covers nine months, so avoid year-over-year claims.

## Decision framework
- Negative monthly revenue: check volume versus AOV contributions, then investigate outlet-level deviations and business context.
- Peak demand: review staffing and opening hours with managers; compare orders per labor hour only if staffing data is collected.
- Basket associations: consider a pilot bundle only if support and lift are credible; track incremental basket value and margin against a comparison group.
- Document actual results in docs/findings.md after real-data execution. Recommendations are proposed actions, not achieved outcomes.

## Repository layout
`run.py` pipeline; `sql/` analytical queries; `tests/` synthetic smoke test; `powerbi/` report instructions, DAX and theme; `docs/` business and validation notes. Raw data and generated files are ignored by Git; share only reviewed outputs with source attribution.
