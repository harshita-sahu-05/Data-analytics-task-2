# Task 2 - Exploratory Data Analysis (EDA) & Business Intelligence

**Internship:** ApexPlanet Software Pvt. Ltd. - Data Analytics (Task 2)
**Tools:** Python (Pandas, Matplotlib, Seaborn, SciPy), SQL (SQLite), PowerPoint

## Objective
Find patterns, trends and relationships in the cleaned sales data (from Task 1), answer business questions with SQL, and propose a KPI dashboard.

## Repository contents

| File / folder | Purpose |
|---|---|
| `EDA_report.md` | **Main report**: statistics, charts, findings, statistical tests, recommendations |
| `sql/business_queries.sql` | 7 business questions written in SQL (joins, CTEs, window functions) |
| `sql/sql_results.md` | Each query with its result table |
| `sql/results/Q1.csv ... Q7.csv` | Raw query outputs |
| `charts/` | 11 charts (histograms, bar charts, box plot, heatmaps, pair plot, scatter, trends) |
| `eda_outputs/` | Summary-statistics tables, correlation matrix, statistical tests, key findings (CSV/JSON) |
| `dashboard_mockup.pptx` | Static dashboard mock-up and proposed KPIs (PowerPoint) |
| `data/cleaned_sales_data.csv` | Input: cleaned dataset from Task 1 |
| `eda.db` | SQLite database (star schema) used by the SQL queries |
| `01_build_db_and_run_sql.py` | Builds the database and runs all queries |
| `02_eda_analysis.py` | Creates the statistics, charts and tests |
| `03_build_dashboard_mockup.py` | Creates the PowerPoint mock-up |

## What was done

1. **Descriptive and univariate analysis:** summary statistics for numeric and categorical fields, histograms, bar charts and box plots.
2. **SQL for business questions:** 7 questions (top products, monthly trend with month-over-month change, last-6-months ranking, city performance, category by age group, gender by category, big-order dependence). The cleaned table is split into a small star schema (`fact_orders`, `dim_product`, `dim_city`, `dim_date`) so the queries use real multi-table joins. All results were cross-checked in Pandas.
3. **Multivariate analysis:** correlation heatmap, pair plot, scatter plot, city x category and age x category heatmaps, plus statistical tests (correlation, chi-square, Kruskal-Wallis, Mann-Whitney).
4. **Dashboard mock-up:** one-page KPI dashboard and a table of 7 proposed KPIs with formulas and reasons.

## Key findings
- Electronics brings **36.4%** of revenue; the other four categories hold 14-18% each.
- Order value depends only on price (r = 0.69) and quantity (r = 0.65); age, gender, city, category and weekday show no statistically significant effect on it.
- The top 20% of orders carry **46.8%** of revenue.
- Revenue is uneven by month (Rs 9.2M in Sep to Rs 13.1M in Mar); Q3 is the weakest quarter.
- Mobile fell from the top product (Jan-Jun) to last (Jul onwards). This is flagged as something to verify, not a proven decline.

## Limitations
The numeric fields are close to uniform and prices look simulated, so the findings mainly show the method. There is no marketing or acquisition data, so those example questions from the task brief could not be answered. Details are in section 7 of the report.

## How to run
```
pip install pandas numpy matplotlib seaborn scipy python-pptx tabulate
python 01_build_db_and_run_sql.py
python 02_eda_analysis.py
python 03_build_dashboard_mockup.py
```
