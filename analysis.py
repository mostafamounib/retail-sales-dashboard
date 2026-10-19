from pathlib import Path
import pandas as pd

data_path = Path(__file__).parent / "retail_sales_dataset.csv"
df = pd.read_csv(data_path)
df["Date"] = pd.to_datetime(df["Date"])

print("FIRST FIVE ROWS")
print(df.head())

print("\nDATA QUALITY")
print("Missing values:", df.isna().sum().sum())
print("Duplicate rows:", df.duplicated().sum())

total_sales = df["Total Amount"].sum()
transactions = df["Transaction ID"].nunique()
units_sold = df["Quantity"].sum()

print("\nSALES SUMMARY")
print(f"Total sales: {total_sales:,.0f}")
print(f"Transactions: {transactions:,}")
print(f"Units sold: {units_sold:,}")
print(f"Average transaction value: {total_sales / transactions:,.2f}")


import matplotlib.pyplot as plt

# Group transactions by category, add their sales, and sort.
category_sales = (
    df.groupby("Product Category")["Total Amount"]
    .sum()
    .sort_values(ascending=False)
)

print("\nSALES BY CATEGORY")
print(category_sales)

# Create a bar chart.
fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    category_sales.index,
    category_sales.values,
    color=["#2563EB", "#60A5FA", "#93C5FD"],
)

ax.set_title("Total Sales by Product Category")
ax.set_xlabel("Product Category")
ax.set_ylabel("Sales — currency unspecified")
ax.bar_label(bars, fmt="%.0f", padding=5)
ax.set_ylim(0, category_sales.max() * 1.15)

fig.tight_layout()

# Save the chart in a folder beside this script.
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)

fig.savefig(output_dir / "sales_by_category.png", dpi=200)
plt.show()


# Keep 2023 transactions for a comparable monthly chart.
sales_2023 = df[df["Date"].dt.year == 2023].copy()

# Add sales together for each month.
monthly_sales = (
    sales_2023.set_index("Date")["Total Amount"]
    .resample("MS")
    .sum()
)

print("\nMONTHLY SALES — 2023")
print(monthly_sales)

# Draw the monthly trend.
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    monthly_sales.index,
    monthly_sales.values,
    marker="o",
    color="#2563EB",
    linewidth=2,
)

ax.set_title("Monthly Sales — 2023")
ax.set_xlabel("Month")
ax.set_ylabel("Sales — currency unspecified")
ax.set_xticks(monthly_sales.index)
ax.set_xticklabels(monthly_sales.index.strftime("%b"))
ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.25)

fig.tight_layout()
fig.savefig(output_dir / "monthly_sales_2023.png", dpi=200)
plt.show()  
