
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Adidas Sales KPI Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. LOAD DATASET
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv("adidas_sales_clean.csv")

    df["Invoice Date"] = pd.to_datetime(
        df["Invoice Date"],
        errors="coerce"
    )

    numeric_columns = [
        "Price per Unit",
        "Units Sold",
        "Total Sales",
        "Operating Profit",
        "Operating Margin"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    return df

df = load_data()

# Periksa kolom yang dibutuhkan
required_columns = [
    "Invoice Date",
    "Region",
    "Product",
    "Retailer",
    "Sales Method",
    "Units Sold",
    "Total Sales",
    "Operating Profit",
    "Operating Margin"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"Kolom berikut tidak ditemukan: {missing_columns}")
    st.stop()

# ==========================================
# 3. DASHBOARD HEADER
# ==========================================

st.title("📊 ADIDAS SALES KPI DASHBOARD")

st.markdown(
    "### Sales Performance & Business Intelligence"
)

st.caption(
    "Data Source: Adidas US Sales Dataset | 2020–2021"
)

st.divider()

# ==========================================
# 4. SIDEBAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

st.sidebar.markdown(
    "Gunakan filter untuk melihat performa penjualan."
)

# Filter tanggal
valid_dates = df["Invoice Date"].dropna()

if valid_dates.empty:
    st.error("Tidak ada tanggal transaksi yang valid.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Invoice Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Invoice Date"].dt.date >= start_date) &
        (filtered_df["Invoice Date"].dt.date <= end_date)
    ]

# Filter Region
regions = sorted(
    df["Region"].dropna().unique().tolist()
)

selected_region = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

if selected_region:
    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_region)
    ]

# Filter Product
products = sorted(
    df["Product"].dropna().unique().tolist()
)

selected_product = st.sidebar.multiselect(
    "Product",
    products,
    default=products
)

if selected_product:
    filtered_df = filtered_df[
        filtered_df["Product"].isin(selected_product)
    ]

# Filter Sales Method
methods = sorted(
    df["Sales Method"].dropna().unique().tolist()
)

selected_method = st.sidebar.multiselect(
    "Sales Method",
    methods,
    default=methods
)

if selected_method:
    filtered_df = filtered_df[
        filtered_df["Sales Method"].isin(selected_method)
    ]

# ==========================================
# 5. KPI CALCULATION
# ==========================================

total_revenue = filtered_df["Total Sales"].sum()

total_profit = filtered_df["Operating Profit"].sum()

total_units = filtered_df["Units Sold"].sum()

total_records = len(filtered_df)

operating_margin = (
    total_profit / total_revenue * 100
    if total_revenue != 0 else 0
)

average_price = (
    total_revenue / total_units
    if total_units != 0 else 0
)

# ==========================================
# 6. KPI CARDS
# ==========================================

st.subheader("Key Performance Indicators")

if filtered_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "Total Operating Profit",
    f"${total_profit:,.0f}"
)

col3.metric(
    "Total Units Sold",
    f"{total_units:,.0f}"
)

col4, col5, col6 = st.columns(3)

col4.metric(
    "Operating Margin",
    f"{operating_margin:.2f}%"
)

col5.metric(
    "Average Selling Price",
    f"${average_price:,.2f}"
)

col6.metric(
    "Sales Records",
    f"{total_records:,}"
)

st.divider()

# ==========================================
# 7. MONTHLY SALES TREND
# ==========================================

st.subheader("Monthly Sales Performance")

monthly_sales = (
    filtered_df
    .assign(
        Month=filtered_df["Invoice Date"].dt.to_period("M").astype(str)
    )
    .groupby("Month", as_index=False)
    .agg(
        Revenue=("Total Sales", "sum"),
        Profit=("Operating Profit", "sum")
    )
)

fig_monthly = px.line(
    monthly_sales,
    x="Month",
    y=["Revenue", "Profit"],
    markers=True,
    title="Monthly Revenue and Profit Trend",
    labels={
        "value": "Amount (USD)",
        "Month": "Month",
        "variable": "Performance"
    }
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

st.divider()

# ==========================================
# 8. SALES BY REGION
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Sales by Region")

    region_sales = (
        filtered_df
        .groupby("Region", as_index=False)
        ["Total Sales"].sum()
        .sort_values("Total Sales", ascending=False)
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Total Sales",
        color="Region",
        title="Revenue by Region"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

# ==========================================
# 9. SALES BY METHOD
# ==========================================

with col2:

    st.subheader("Sales by Method")

    method_sales = (
        filtered_df
        .groupby("Sales Method", as_index=False)
        ["Total Sales"].sum()
    )

    fig_method = px.pie(
        method_sales,
        names="Sales Method",
        values="Total Sales",
        hole=0.4,
        title="Revenue Distribution by Sales Method"
    )

    st.plotly_chart(
        fig_method,
        use_container_width=True
    )

st.divider()

# ==========================================
# 10. PRODUCT PERFORMANCE
# ==========================================

st.subheader("Product Performance")

product_sales = (
    filtered_df
    .groupby("Product", as_index=False)
    .agg(
        Revenue=("Total Sales", "sum"),
        Profit=("Operating Profit", "sum"),
        Units=("Units Sold", "sum")
    )
    .sort_values("Revenue", ascending=False)
)

fig_product = px.bar(
    product_sales.head(5),
    x="Revenue",
    y="Product",
    orientation="h",
    color="Revenue",
    title="Top 5 Products by Revenue"
)

fig_product.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(
    fig_product,
    use_container_width=True
)

st.divider()

# ==========================================
# 11. RETAILER PERFORMANCE
# ==========================================

st.subheader("Top 5 Retailers")

retailer_sales = (
    filtered_df
    .groupby("Retailer", as_index=False)
    ["Total Sales"].sum()
    .sort_values("Total Sales", ascending=False)
    .head(5)
)

fig_retailer = px.bar(
    retailer_sales,
    x="Retailer",
    y="Total Sales",
    color="Total Sales",
    title="Top 5 Retailers by Revenue"
)

st.plotly_chart(
    fig_retailer,
    use_container_width=True
)

st.divider()

# ==========================================
# 12. SALES DATA TABLE
# ==========================================

st.subheader("Sales Transaction Details")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 13. DOWNLOAD FILTERED DATA
# ==========================================

csv = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="adidas_sales_filtered.csv",
    mime="text/csv"
)

# ==========================================
# 14. FOOTER
# ==========================================

st.divider()

st.caption(
    "Adidas Sales KPI Dashboard | "
    "Developed using Python, Pandas, Plotly and Streamlit"
)
