from pathlib import Path
import sqlite3
import pandas as pd

project_dir = Path(__file__).parent
df = pd.read_csv(project_dir / "retail_sales_dataset.csv")

# Use simple column names for SQL.
df.columns = (
    df.columns.str.lower()
    .str.replace(" ", "_", regex=False)
)

query = """
SELECT
    product_category,
    SUM(total_amount) AS total_sales,
    COUNT(DISTINCT transaction_id) AS transactions,
    SUM(quantity) AS units_sold,
    ROUND(
        SUM(total_amount) * 1.0 / COUNT(DISTINCT transaction_id),
        2
    ) AS avg_transaction_value
FROM sales
WHERE date >= '2023-01-01'
  AND date < '2024-01-01'
GROUP BY product_category
ORDER BY total_sales DESC;
"""

# Create a local database and load the CSV into a table.
with sqlite3.connect(project_dir / "retail_sales.db") as connection:
    df.to_sql("sales", connection, if_exists="replace", index=False)
    results = pd.read_sql_query(query, connection)

print("CATEGORY PERFORMANCE — SQL")
print(results.to_string(index=False))

# Compare SQL revenue with an independent pandas calculation.
sales_2023 = df[
    (df["date"] >= "2023-01-01") &
    (df["date"] < "2024-01-01")
]

pandas_totals = (
    sales_2023.groupby("product_category")["total_amount"]
    .sum()
    .sort_index()
)

sql_totals = (
    results.set_index("product_category")["total_sales"]
    .sort_index()
)

pd.testing.assert_series_equal(
    pandas_totals,
    sql_totals,
    check_names=False,
)

print("\nCheck passed: SQL and pandas category sales match.")
