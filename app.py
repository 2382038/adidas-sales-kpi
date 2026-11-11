
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Adidas | Sales Performance",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F4F4F2;
    color: #171717;
}

[data-testid="stSidebar"] {
    background-color: #171717;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #333333 !important;
}

[data-testid="stSidebar"] input {
    color: #171717 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #171717;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.main-header {
    background: #171717;
    padding: 30px 35px;
    border-radius: 5px;
    color: white;
    margin-bottom: 25px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.brand-name {
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -2px;
    color: white;
}

.header-subtitle {
    color: #C8C8C8;
    font-size: 13px;
    margin-top: 5px;
}

.header-label {
    color: #FFFFFF;
    font-size: 11px;
    letter-spacing: 2px;
    border: 1px solid #666666;
    padding: 8px 12px;
}

.section-heading {
    font-size: 21px;
    font-weight: 800;
    color: #171717;
    margin-top: 15px;
    margin-bottom: 4px;
}

.section-description {
    color: #777777;
    font-size: 12px;
    margin-bottom: 18px;
}

.kpi-card {
    background: #FFFFFF;
    padding: 20px;
    border-left: 4px solid #171717;
    border-radius: 4px;
    min-height: 115px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.035);
}

.kpi-label {
    color: #777777;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.kpi-value {
    color: #171717;
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
}

.kpi-card.red {
    border-left-color: #E32636;
}

.chart-container {
    background: #FFFFFF;
    border-radius: 5px;
    padding: 15px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 17px 18px;
    border-radius: 4px;
    border-left: 4px solid #171717;
    box-shadow: 0 2px 8px rgba(0,0,0,0.035);
}

div[data-testid="stMetricLabel"] {
    color: #777777;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #171717;
    font-weight: 800;
}

.stButton button, .stDownloadButton button {
    background-color: #171717;
    color: white;
    border-radius: 3px;
    border: none;
    font-weight: 600;
}

.stButton button:hover, .stDownloadButton button:hover {
    background-color: #E32636;
    color: white;
}

hr {
    border-color: #DDDDDD;
}

.footer {
    text-align: center;
    color: #888888;
    font-size: 11px;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOAD DATASET
# ==========================================

@st.cache_data
def load_data():
    df = pd.read_csv("adidas_sales_clean.csv")

    df["Invoice Date"] = pd.to_datetime(
        df["Invoice Date"], errors="coerce"
    )

    numeric_columns = [
        "Price per Unit",
        "Units Sold",
        "Total Sales",
        "Operating Profit",
        "Operating Margin"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

required_columns = [
    "Invoice Date", "Region", "Product", "Retailer",
    "Sales Method", "Units Sold", "Total Sales",
    "Operating Profit", "Operating Margin"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Kolom tidak ditemukan: {missing_columns}")
    st.stop()

# ==========================================
# 4. DASHBOARD HEADER + ADIDAS STYLE LOGO
# ==========================================

st.markdown("""
<div class="main-header">
    <div class="brand">
        <img
            src="https://cdn.simpleicons.org/adidas/FFFFFF"
            width="85"
            style="object-fit:contain;"
        >
        <div>
            <div class="brand-name">adidas</div>
            <div class="header-subtitle">
                SALES PERFORMANCE & BUSINESS INTELLIGENCE
            </div>
        </div>
    </div>
    <div class="header-label">US MARKET / 2020—2021</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. SIDEBAR FILTERS
# ==========================================

st.sidebar.markdown("## ADIDAS")
st.sidebar.caption("SALES ANALYTICS")
st.sidebar.divider()

st.sidebar.markdown("### FILTER DATA")
st.sidebar.caption("Select the criteria to explore sales performance.")

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

regions = sorted(df["Region"].dropna().unique().tolist())

selected_region = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

filtered_df = filtered_df[
    filtered_df["Region"].isin(selected_region)
]

products = sorted(df["Product"].dropna().unique().tolist())

selected_product = st.sidebar.multiselect(
    "Product",
    products,
    default=products
)

filtered_df = filtered_df[
    filtered_df["Product"].isin(selected_product)
]

methods = sorted(df["Sales Method"].dropna().unique().tolist())

selected_method = st.sidebar.multiselect(
    "Sales Method",
    methods,
    default=methods
)

filtered_df = filtered_df[
    filtered_df["Sales Method"].isin(selected_method)
]

st.sidebar.divider()
st.sidebar.caption("ADIDAS SALES DATASET")
st.sidebar.caption("Source: Adidas US Sales Dataset")

# ==========================================
# 6. CHECK FILTERED DATA
# ==========================================

if filtered_df.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih.")
    st.stop()

# ==========================================
# 7. KPI CALCULATION
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
# 8. KPI SECTION
# ==========================================

st.markdown(
    '<div class="section-heading">BUSINESS OVERVIEW</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'A snapshot of Adidas sales performance based on selected filters.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

col1.metric("TOTAL REVENUE", f"${total_revenue:,.0f}")
col2.metric("OPERATING PROFIT", f"${total_profit:,.0f}")
col3.metric("UNITS SOLD", f"{total_units:,.0f}")

col4, col5, col6 = st.columns(3)

col4.metric("OPERATING MARGIN", f"{operating_margin:.2f}%")
col5.metric("AVERAGE SELLING PRICE", f"${average_price:,.2f}")
col6.metric("SALES RECORDS", f"{total_records:,}")

st.divider()

# ==========================================
# 9. MONTHLY SALES PERFORMANCE
# ==========================================

st.markdown(
    '<div class="section-heading">01 / SALES TREND</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Monthly comparison of revenue and operating profit.'
    '</div>',
    unsafe_allow_html=True
)

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
    .sort_values("Month")
)

fig_monthly = px.line(
    monthly_sales,
    x="Month",
    y=["Revenue", "Profit"],
    markers=True,
    color_discrete_sequence=["#171717", "#E32636"],
    labels={
        "value": "Amount (USD)",
        "Month": "Month",
        "variable": "Metric"
    }
)

fig_monthly.update_layout(
    template="plotly_white",
    height=390,
    margin=dict(l=20, r=20, t=25, b=20),
    legend_title_text="",
    hovermode="x unified"
)

fig_monthly.update_traces(line=dict(width=3))

st.plotly_chart(
    fig_monthly,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.divider()

# ==========================================
# 10. REGION & SALES METHOD
# ==========================================

st.markdown(
    '<div class="section-heading">02 / SALES DISTRIBUTION</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Explore how revenue is distributed across regions and sales channels.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("**Revenue by Region**")

    region_sales = (
        filtered_df
        .groupby("Region", as_index=False)["Total Sales"]
        .sum()
        .sort_values("Total Sales", ascending=True)
    )

    fig_region = px.bar(
        region_sales,
        x="Total Sales",
        y="Region",
        orientation="h",
        color_discrete_sequence=["#171717"],
        labels={
            "Total Sales": "Revenue (USD)",
            "Region": ""
        }
    )

    fig_region.update_layout(
        template="plotly_white",
        height=350,
        margin=dict(l=10, r=10, t=20, b=20),
        showlegend=False
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
        config={"displayModeBar": False}
    )

with col2:

    st.markdown("**Revenue by Sales Method**")

    method_sales = (
        filtered_df
        .groupby("Sales Method", as_index=False)["Total Sales"]
        .sum()
    )

    fig_method = px.pie(
        method_sales,
        names="Sales Method",
        values="Total Sales",
        hole=0.55,
        color_discrete_sequence=["#171717", "#777777", "#E32636"]
    )

    fig_method.update_layout(
        template="plotly_white",
        height=350,
        margin=dict(l=10, r=10, t=20, b=20),
        legend_title_text=""
    )

    st.plotly_chart(
        fig_method,
        use_container_width=True,
        config={"displayModeBar": False}
    )

st.divider()

# ==========================================
# 11. PRODUCT PERFORMANCE
# ==========================================

st.markdown(
    '<div class="section-heading">03 / PRODUCT PERFORMANCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Identify the products contributing the highest revenue.'
    '</div>',
    unsafe_allow_html=True
)

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
    product_sales.head(5).sort_values("Revenue"),
    x="Revenue",
    y="Product",
    orientation="h",
    text_auto=",.0f",
    color_discrete_sequence=["#E32636"],
    labels={
        "Revenue": "Revenue (USD)",
        "Product": ""
    }
)

fig_product.update_layout(
    template="plotly_white",
    height=350,
    margin=dict(l=10, r=20, t=20, b=20),
    showlegend=False
)

st.plotly_chart(
    fig_product,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.divider()

# ==========================================
# 12. RETAILER PERFORMANCE
# ==========================================

st.markdown(
    '<div class="section-heading">04 / RETAILER PERFORMANCE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Top five retailers ranked by total revenue.'
    '</div>',
    unsafe_allow_html=True
)

retailer_sales = (
    filtered_df
    .groupby("Retailer", as_index=False)["Total Sales"]
    .sum()
    .sort_values("Total Sales", ascending=True)
    .tail(5)
)

fig_retailer = px.bar(
    retailer_sales,
    x="Total Sales",
    y="Retailer",
    orientation="h",
    text_auto=",.0f",
    color_discrete_sequence=["#171717"],
    labels={
        "Total Sales": "Revenue (USD)",
        "Retailer": ""
    }
)

fig_retailer.update_layout(
    template="plotly_white",
    height=350,
    margin=dict(l=10, r=20, t=20, b=20),
    showlegend=False
)

st.plotly_chart(
    fig_retailer,
    use_container_width=True,
    config={"displayModeBar": False}
)

st.divider()

# ==========================================
# 13. TRANSACTION DETAILS
# ==========================================

st.markdown(
    '<div class="section-heading">05 / TRANSACTION DETAILS</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Detailed records based on the selected filters.'
    '</div>',
    unsafe_allow_html=True
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="DOWNLOAD FILTERED DATA",
    data=csv,
    file_name="adidas_sales_filtered.csv",
    mime="text/csv"
)

# ==========================================
# 14. FOOTER
# ==========================================

st.markdown("""
<div class="main-header">
    <div class="brand">
        <img
            src="https://cdn.simpleicons.org/adidas/FFFFFF"
            width="85"
            style="object-fit:contain;"
        >
        <div>
            <div class="brand-name">adidas</div>
            <div class="header-subtitle">
                SALES PERFORMANCE & BUSINESS INTELLIGENCE
            </div>
        </div>
    </div>
    <div class="header-label">US MARKET / 2020—2021</div>
</div>
""", unsafe_allow_html=True)