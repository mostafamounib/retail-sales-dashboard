from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")

# Load the dataset.
data_path = Path(__file__).parent / "retail_sales_dataset.csv"
df = pd.read_csv(data_path)
df["Date"] = pd.to_datetime(df["Date"])

st.title("Retail Sales Dashboard")
st.caption(
    "2023 sales analysis • Currency unspecified in the source data. "
    "January 1, 2024 is excluded from all dashboard metrics and charts."
)

# Use the same reporting period throughout the dashboard.
df = df[df["Date"].dt.year == 2023].copy()

# Let the user choose categories.
categories = sorted(df["Product Category"].unique())

selected_categories = st.sidebar.multiselect(
    "Product categories",
    options=categories,
    default=categories,
)

filtered = df[df["Product Category"].isin(selected_categories)]

if filtered.empty:
    st.info("Select at least one category to see the dashboard.")
    st.stop()

# Calculate metrics using only the selected data.
sales = filtered["Total Amount"].sum()
transactions = filtered["Transaction ID"].nunique()
units = filtered["Quantity"].sum()

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

col1.metric("Total sales", f"{sales:,.0f}")
col2.metric("Transactions", f"{transactions:,}")
col3.metric("Units sold", f"{units:,}")
col4.metric("Avg. transaction value", f"{sales / transactions:,.2f}")

# Prepare category and monthly totals.
category_sales = (
    filtered.groupby("Product Category")["Total Amount"]
    .sum()
)

monthly_sales = (
    filtered.set_index("Date")["Total Amount"]
    .resample("MS")
    .sum()
    .reindex(pd.date_range("2023-01-01", "2023-12-01", freq="MS"),
             fill_value=0)
)

left, right = st.columns(2)

with left:
    st.subheader("Sales by category")
    st.bar_chart(category_sales)

with right:
    st.subheader("Monthly sales")
    st.line_chart(monthly_sales)

with st.expander("View filtered transactions"):
    st.dataframe(filtered, hide_index=True) 


st.subheader("Category performance")

category_summary = (
    filtered.groupby("Product Category")
    .agg(
        Sales=("Total Amount", "sum"),
        Transactions=("Transaction ID", "nunique"),
        Units=("Quantity", "sum"),
    )
    .sort_values("Sales", ascending=False)
)

category_summary["Avg. transaction value"] = (
    category_summary["Sales"] / category_summary["Transactions"]
)

category_summary["Sales share (%)"] = (
    category_summary["Sales"] / category_summary["Sales"].sum() * 100
)

st.caption("Sales share is calculated within the selected categories.")

st.dataframe(
    category_summary.style.format({
        "Sales": "{:,.0f}",
        "Transactions": "{:,.0f}",
        "Units": "{:,.0f}",
        "Avg. transaction value": "{:,.2f}",
        "Sales share (%)": "{:.1f}%",
    })
)