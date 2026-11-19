"""Task 2 - Step 1: build a SQLite star schema from the cleaned data and run the business queries.

Input : data/cleaned_sales_data.csv  (output of Task 1)
Output: eda.db, sql/results/Q*.csv, sql/sql_results.md
Run   : python 01_build_db_and_run_sql.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
CSV = BASE / "data" / "cleaned_sales_data.csv"
DB = BASE / "eda.db"
SQL_FILE = BASE / "sql" / "business_queries.sql"
OUT = BASE / "sql" / "results"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(CSV)

# ------------------------------------------------------------ build star schema
dim_product = (df[["Product", "Category"]].drop_duplicates().sort_values("Product").reset_index(drop=True))
dim_product.insert(0, "product_id", dim_product.index + 1)
dim_product.columns = ["product_id", "product", "category"]

dim_city = pd.DataFrame({"city": sorted(df["City"].unique())})
dim_city.insert(0, "city_id", dim_city.index + 1)

dim_date = (df[["Order_Date", "Order_Year", "Order_Month", "Month_Name", "Quarter", "Weekday", "Is_Weekend"]]
            .drop_duplicates().sort_values("Order_Date"))
dim_date.columns = ["date", "year", "month", "month_name", "quarter", "weekday", "is_weekend"]
dim_date["is_weekend"] = dim_date["is_weekend"].astype(int)

fact = (df.merge(dim_product, left_on=["Product", "Category"], right_on=["product", "category"])
          .merge(dim_city, left_on="City", right_on="city"))
fact = fact.rename(columns={"Order_ID": "order_id", "Order_Date": "order_date", "Customer_ID": "customer_id",
                            "Age": "age", "Age_Imputed": "age_imputed", "Gender": "gender", "Quantity": "quantity",
                            "Unit_Price": "unit_price", "Total_Sales": "total_sales"})
fact["age_imputed"] = fact["age_imputed"].astype(int)
fact = fact[["order_id", "order_date", "customer_id", "age", "age_imputed", "gender", "city_id", "product_id",
             "quantity", "unit_price", "total_sales"]]
assert len(fact) == len(df) == 1000, "row count changed during joins"

if DB.exists():
    DB.unlink()
con = sqlite3.connect(DB)
for name, t in [("dim_product", dim_product), ("dim_city", dim_city), ("dim_date", dim_date), ("fact_orders", fact)]:
    t.to_sql(name, con, index=False)
con.execute("CREATE INDEX ix_fact_date ON fact_orders(order_date)")
con.execute("CREATE INDEX ix_fact_product ON fact_orders(product_id)")
con.commit()

# ------------------------------------------------------------ run queries
text = SQL_FILE.read_text(encoding="utf-8")
blocks = re.split(r"(?m)^-- (Q\d+): ", text)[1:]          # [name, body, name, body, ...]
md = ["# SQL Results\n", "Database: SQLite, star schema (`fact_orders` + `dim_product`, `dim_city`, `dim_date`).\n"]
for name, body in zip(blocks[0::2], blocks[1::2]):
    question = body.splitlines()[0].strip()
    sql = "\n".join(l for l in body.splitlines()[1:] if not l.startswith("-- Skills")).strip()
    res = pd.read_sql_query(sql, con)
    res.to_csv(OUT / f"{name}.csv", index=False)
    md.append(f"\n## {name}: {question}\n")
    md.append("```sql\n" + sql + "\n```\n")
    shown = res.copy()
    for c in shown.select_dtypes("float").columns:       # whole-number floats -> thousands-separated ints
        if (shown[c].dropna() % 1 == 0).all():
            shown[c] = shown[c].map(lambda v: "" if pd.isna(v) else f"{int(v):,}")
    md.append(shown.to_markdown(index=False, disable_numparse=True) + "\n")
    print(f"{name}: {len(res)} rows")
con.close()
(BASE / "sql" / "sql_results.md").write_text("\n".join(md), encoding="utf-8")
print("done")
