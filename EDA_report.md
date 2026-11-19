# Exploratory Data Analysis Report

**Dataset:** `cleaned_sales_data.csv` from Task 1 (1,000 orders, 1 Jan 2025 - 1 Jan 2026, 8 cities, 6 products in 5 categories)
**Tools:** Python (Pandas, Matplotlib, Seaborn, SciPy), SQLite, PowerPoint
**All figures are in INR.** K = thousand, L = lakh (100K), M = million.

## 1. Summary of findings

1. **Electronics is the largest category.** It brings 36.4% of revenue (Laptop and Mobile together); the other four categories hold 14-18% each.
2. **Mobile slipped from first to last.** It was the top product in Jan-Jun 2025 (Rs 15.4M, 106 orders) but is last from July onwards (Rs 9.9M, 78 orders), while Laptop and Book lead. Treat this as a lead to check, not a proven decline: on its own the drop is statistically detectable (p = 0.026), but Mobile was picked after looking at six products, and the overall product mix did not change significantly (p = 0.27).
3. **Revenue is uneven month to month.** It ranges from Rs 9.2M (Sep) to Rs 13.1M (Mar). Q3 is the weakest quarter (Rs 30.4M) and Q4 the strongest (Rs 37.4M).
4. **Order value is driven only by price and quantity.** Total_Sales correlates with Unit_Price (r = 0.69) and Quantity (r = 0.65). Age, gender, city, category and weekday show no statistically significant link with order value.
5. **Revenue is concentrated in big orders.** The top 20% of orders bring 46.8% of revenue.
6. **Cities differ in volume more than in order value.** Patna leads on revenue (Rs 19.3M) because it has the most orders (135); Gaya and Pune trail with about 10% of revenue each. Order value does not differ significantly across cities (p = 0.55).

## 2. Descriptive statistics and univariate analysis

### 2.1 Numeric fields

| Field | Mean | Median | Std dev | Min | Max | Skew |
|---|---|---|---|---|---|---|
| Age | 41.4 | 41 | 13.7 | 18 | 65 | 0.04 |
| Quantity | 5.4 | 5 | 2.8 | 1 | 10 | 0.06 |
| Unit_Price | 25,487 | 25,399 | 14,179 | 146 | 49,998 | -0.03 |
| Total_Sales | 139,399 | 108,594 | 114,100 | 437 | 493,678 | 0.99 |

![Histograms](charts/01_histograms_numeric.png)

**Interpretation**
- Age, Quantity and Unit_Price are close to flat (uniform) across their ranges, with mean about equal to median and skew near 0. Real retail data usually looks more lopsided, so this dataset behaves like a simulated one. That is worth saying openly in the video.
- Total_Sales is right-skewed (skew 0.99): the mean (139K) is well above the median (109K) because a minority of large orders pull it up. **Use the median alongside the average when reporting order value.**
- Total_Sales is Quantity x Unit_Price, so its shape comes from multiplying two independent flat variables.

### 2.2 Categorical fields

![Counts](charts/02_bar_categorical_counts.png)

| Field | What the counts show |
|---|---|
| Category | Electronics 354 orders (35%), Education 178, Furniture 159, Fashion 156, Grocery 153. Electronics has two products, which explains its size. |
| City | Patna 135, Kolkata 133, Mumbai 131 ... Pune 99. 13 orders have an unknown city. |
| Gender | Male 511 (51%), Female 489 (49%): balanced. |
| Age group | 35-44 (225) and 55+ (223) are the largest; 18-24 is the smallest (147). |

![Revenue by category and product](charts/03_bar_revenue_category_product.png)

| Product | Revenue (M) | Share |
|---|---|---|
| Laptop | 25.4 | 18.3% |
| Mobile | 25.3 | 18.2% |
| Book | 25.0 | 18.0% |
| Rice | 22.2 | 15.9% |
| Chair | 21.5 | 15.4% |
| Shoes | 19.8 | 14.2% |

![Order value by category](charts/04_box_order_value_by_category.png)

Order-value distributions look alike in every category (Kruskal-Wallis p = 0.73), so categories differ in how many orders they receive, not in how big each order is.

### 2.3 Time

![Monthly trend](charts/05_monthly_trend.png)

- Revenue peaks in March (Rs 13.1M) and June (Rs 12.9M) and bottoms out in August-September (Rs 9.4M and 9.2M). October rebounds by 36% and stays near Rs 12.5M until December.
- Variation between months is moderate (coefficient of variation 11.6%).
- January 2026 has only 5 orders (the data ends on 1 Jan), so it is left out of monthly charts.
- Orders per weekday range from 126 (Tue) to 153 (Sun). This spread is consistent with chance (chi-square goodness-of-fit p = 0.72), so no weekday effect is claimed.

![Weekday](charts/11_bar_weekday.png)

## 3. SQL for business questions

Seven business questions are answered in `sql/business_queries.sql`; the full output is in `sql/sql_results.md`. The data is loaded into a small SQLite star schema (`fact_orders` joined to `dim_product`, `dim_city`, `dim_date`) so the queries use real multi-table joins. The queries use JOINs, GROUP BY, HAVING, CTEs and window functions (LAG, RANK). Every result was cross-checked against Pandas.

| # | Business question | Answer |
|---|---|---|
| Q1 | Top 5 products by revenue? | Laptop (25.4M), Mobile (25.3M), Book (25.0M), Rice (22.2M), Chair (21.5M) |
| Q2 | Monthly trend and month-over-month change? | Biggest drop Aug (-19.6%), biggest rise Oct (+36.2%). The Jan 2026 row (-93.4%) is a 5-order partial month and should be ignored. |
| Q3 | Top 5 products in the last 6 months? | Laptop, Book, Chair, Shoes, Rice. Mobile drops out of the top 5 (6th of 6). |
| Q4 | Which cities earn the most, and their average order value? | Patna 19.3M first. Bengaluru has the highest average order (153.9K), Gaya the lowest (122.9K). |
| Q5 | Revenue by category across age groups? | Electronics is the top category in every age group. 55+ is the highest-revenue group (30.5M). |
| Q6 | Gender differences per category? | Men order more Electronics (196 vs 158), women more Fashion (89 vs 67). The overall gender-category association is not significant at 5% (p = 0.059). |
| Q7 | Which categories depend on big orders? | In every category, the 38-43% of orders above the category average carry 70-76% of its revenue. Grocery is the highest (76.2%). |

## 4. Multivariate analysis and correlation

![Correlation heatmap](charts/06_heatmap_correlation.png)

![Pair plot](charts/07_pairplot_numeric.png)

![Scatter](charts/08_scatter_price_vs_sales.png)

- **Order value vs price and quantity:** r = 0.69 and 0.65. The pair plot shows the "fan" of straight lines, one per quantity from 1 to 10: each line is a fixed number of units.
- **Price vs quantity:** r = 0.02. Customers do not buy fewer units of expensive items, so order value is not self-limiting.
- **Age vs everything:** r is between -0.03 and 0.00. Age does not explain price, quantity or order value.

![City x category](charts/09_heatmap_city_category.png)

Electronics is the biggest cell in every city (4.8M in Gaya to 7.7M in Kolkata). Fashion is strongest in Bengaluru (4.0M) and weakest in Kolkata and Hyderabad (1.9M each).

![Age x category](charts/10_heatmap_age_category.png)

The category mix looks different by age group (Electronics 32% for 18-24 vs 41% for 25-34; Fashion 17-18% for the youngest and oldest groups vs 11% for 25-34), but a chi-square test finds the differences are within what chance produces (p = 0.88, Cramer's V = 0.05). **There is no reliable evidence that age changes what people buy.**

### Statistical checks

| Test | Result | Reading |
|---|---|---|
| Pearson / Spearman: Unit_Price vs Total_Sales | r = 0.686, p < 0.0001 | significant |
| Pearson / Spearman: Quantity vs Total_Sales | r = 0.647, p < 0.0001 | significant |
| Pearson / Spearman: Age vs Total_Sales | r = 0.001, p = 0.97 | no relationship |
| Chi-square: age group vs category | chi2 = 9.8, p = 0.88 | not significant |
| Chi-square: gender vs category | chi2 = 9.1, p = 0.059 | borderline, not significant at 5% |
| Kruskal-Wallis: order value across categories | p = 0.73 | not significant |
| Kruskal-Wallis: order value across cities | p = 0.55 | not significant |
| Mann-Whitney: male vs female order value | p = 0.65 | not significant |
| Mann-Whitney: weekend vs weekday order value | p = 0.22 | not significant |
| Chi-square: Mobile share of orders, Jan-Jun vs Jul-Jan | 106 -> 78 orders, p = 0.026 | significant on its own, but 1 of 6 products inspected after the fact |
| Chi-square: product mix, Jan-Jun vs Jul-Jan (all 6 products) | chi2 = 6.4, p = 0.27 | no significant change |

The full table is in `eda_outputs/statistical_tests.csv`. With 13 tests at the 5% level, about one spurious "significant" result is expected by chance, so a single p-value near 0.03-0.06 (Mobile, gender vs category) should not be over-read.

## 5. Dashboard mock-up and proposed KPIs

`dashboard_mockup.pptx` holds a one-page dashboard mock-up (KPI tiles, monthly trend, category, city, age group, weekday) and a table of the proposed KPIs.

| KPI | Formula | Why |
|---|---|---|
| Total revenue | SUM(Total_Sales) | Headline size |
| Orders | COUNT(Order_ID) | Demand volume |
| Average order value (and median) | Revenue / Orders | Order value is skewed |
| MoM revenue growth | (This month - last month) / last month | Revenue is volatile |
| Category revenue share | Category / total | Dependence on Electronics |
| High-value order share | Revenue from orders above Q3 + 1.5 x IQR | Concentration risk |
| Data completeness | % of orders with known City and Age | Trust in regional and age cuts |

## 6. Business recommendations

1. **Check Mobile's second-half drop** (15.4M to 9.9M; 106 to 78 orders): look at stock, pricing and competing launches. It may be noise, so confirm with the next quarter's data before acting.
2. **Plan for the Aug-Sep dip.** Revenue fell 20% in August and stayed low in September; a promotion or campaign in these months could smooth revenue.
3. **Protect the large orders.** About 40% of orders carry 70%+ of revenue in every category, so account management or bundles for big buyers would pay off.
4. **Grow order counts in Pune and Gaya.** Their order values are not lower in a statistically meaningful way; they simply have fewer orders (99 and 117 vs 135 in Patna).
5. **Do not target by age or gender yet.** The data shows no reliable difference in order value or category preference between groups.

## 7. Limitations
- Age, Quantity and Unit_Price are close to uniform, and Unit_Price ranges from about 150 to 50,000 for every product, so prices do not look like real catalogue prices. Treat the findings as an exercise in method.
- Customer_ID is not a reliable person key (52 IDs show different names/ages/cities), so no repeat-customer or retention analysis is attempted.
- The dataset has no marketing spend or user-acquisition table, so questions like "marketing spend vs sales" cannot be answered; the multi-table joins use a star schema derived from the one source table.
- 20 orders had an imputed age and 13 an unknown city; age and city analyses exclude them.
