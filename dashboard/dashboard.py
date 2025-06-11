import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="E-Commerce Real-Time Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Automatically refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="dashboard_autorefresh")

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_all_transactions():
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/all", timeout=5)
        response.raise_for_status()
        data = response.json().get("all_transactions", [])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error fetching transactions: {e}")
        return pd.DataFrame()

# Load data
df_all = get_all_transactions()
if df_all.empty:
    st.warning("No transaction data available yet.")
    st.stop()

# Convert timestamp
df_all["timestamp"] = pd.to_datetime(df_all["timestamp"])

# Sidebar filters
st.sidebar.header("🔍 Filter Options")
filters = {
    "product_category": sorted(df_all["product_category"].dropna().unique()),
    "payment_method": sorted(df_all["payment_method"].dropna().unique()),
    "loyalty_tier": sorted(df_all["loyalty_tier"].dropna().unique()),
    "channel": sorted(df_all["channel"].dropna().unique()),
}

selected_categories = st.sidebar.multiselect("Product Categories", filters["product_category"], default=filters["product_category"])
selected_methods = st.sidebar.multiselect("Payment Methods", filters["payment_method"], default=filters["payment_method"])
selected_loyalty = st.sidebar.multiselect("Loyalty Tier", filters["loyalty_tier"], default=filters["loyalty_tier"])
selected_channels = st.sidebar.multiselect("Sales Channel", filters["channel"], default=filters["channel"])

df_filtered = df_all[
    (df_all["product_category"].isin(selected_categories)) &
    (df_all["payment_method"].isin(selected_methods)) &
    (df_all["loyalty_tier"].isin(selected_loyalty)) &
    (df_all["channel"].isin(selected_channels))
]

# Title
st.title("🛒 E-Commerce Real-Time Dashboard")

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    total_revenue = df_filtered["order_total"].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
with col2:
    tx_count = df_filtered.shape[0]
    discounted = df_filtered[df_filtered["discount_percent"] > 0].shape[0]
    percent = (discounted / tx_count * 100) if tx_count else 0
    st.metric("Discount Usage", f"{percent:.1f}%")
    st.caption(f"{discounted} of {tx_count} transactions")
with col3:
    aov = total_revenue / tx_count if tx_count else 0
    st.metric("Avg. Order Value", f"${aov:,.2f}")

# Latest transactions table
st.markdown("### 🔁 Latest Transactions")
st.dataframe(df_filtered.sort_values("timestamp", ascending=False).head(10), use_container_width=True)

# Revenue by Day
st.markdown("### 📈 Daily Revenue")
df_daily = df_filtered.copy()
df_daily["date"] = df_daily["timestamp"].dt.date
df_revenue = df_daily.groupby("date")["order_total"].sum().reset_index()
fig = px.line(df_revenue, x="date", y="order_total",
              title="Revenue by Day",
              labels={"date": "Date", "order_total": "Revenue ($)"})
st.plotly_chart(fig, use_container_width=True)

# Product performance
st.markdown("### 📦 Product Performance")
df_product = df_filtered.groupby(["product_name", "product_category"], as_index=False)["order_total"].sum()
fig_prod = px.bar(df_product, x="product_name", y="order_total", color="product_category",
                  title="Revenue by Product",
                  labels={"order_total": "Revenue ($)", "product_name": "Product"})
fig_prod.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_prod, use_container_width=True)

# Two-column charts
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🎯 Revenue by Loyalty Tier")
    df_loyalty = df_filtered.groupby("loyalty_tier")["order_total"].sum().reset_index()
    fig_loyalty = px.bar(df_loyalty, x="loyalty_tier", y="order_total",
                         title="Revenue by Loyalty Tier",
                         labels={"order_total": "Revenue ($)"})
    st.plotly_chart(fig_loyalty, use_container_width=True)

with col2:
    st.markdown("### 🧾 Payment Method Distribution")
    df_pay = df_filtered["payment_method"].value_counts().reset_index()
    df_pay.columns = ["payment_method", "count"]
    fig_pay = px.pie(df_pay, names="payment_method", values="count",
                     title="Payment Methods")
    st.plotly_chart(fig_pay, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown("### 🌍 Revenue by Region")
    df_region = df_filtered.groupby("customer_region")["order_total"].sum().reset_index()
    fig_region = px.bar(df_region, x="customer_region", y="order_total",
                        title="Revenue by Region",
                        labels={"order_total": "Revenue ($)"})
    st.plotly_chart(fig_region, use_container_width=True)

with col4:
    st.markdown("### 🛒 Sales by Channel")
    df_channel = df_filtered.groupby("channel")["order_total"].sum().reset_index()
    fig_channel = px.pie(df_channel, names="channel", values="order_total",
                         title="Sales by Channel")
    st.plotly_chart(fig_channel, use_container_width=True)

# Sidebar control
with st.sidebar:
    st.header("🧭 Dashboard Controls")
    if st.button("🔄 Manual Refresh"):
        st.rerun()
