import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #202136;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Load and prepare data with error handling
@st.cache_data
def load_data(dataset_path):
    if not os.path.exists(dataset_path):
        st.error(f"Dataset not found at path: {dataset_path}")
        st.stop()
        
    df = pd.read_csv(dataset_path)
    
    # Handle missing values in timestamp column
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    
    # Handle missing values in product_category_name
    df['product_category_name'] = df['product_category_name'].fillna('Unknown Category')
    
    # Handle missing values in numeric columns
    numeric_columns = ['price', 'freight_value', 'product_weight_g']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())
    
    return df

# Load data
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, 'main_dataset.csv')
main_dataset = load_data(dataset_path)

# Verify required columns
required_columns = ['order_purchase_timestamp', 'product_category_name', 'price', 'product_id', 'freight_value', 'product_weight_g']
missing_columns = [col for col in required_columns if col not in main_dataset.columns]
if missing_columns:
    st.error(f"Missing required columns in the dataset: {missing_columns}")
    st.stop()

# Sidebar filters
st.sidebar.title("📊 Dashboard Controls")

# Safe date range selection
min_date = main_dataset['order_purchase_timestamp'].min().date()
max_date = main_dataset['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category filter
all_categories = sorted(main_dataset['product_category_name'].unique().tolist())
if st.sidebar.checkbox("Select All Categories", True):
    selected_categories = all_categories
else:
    selected_categories = st.sidebar.multiselect(
        "Select Categories",
        options=all_categories,
        default=all_categories[:5] if len(all_categories) >= 5 else all_categories
    )

# Apply filters
filtered_data = main_dataset[
    (main_dataset['order_purchase_timestamp'].dt.date >= date_range[0]) &
    (main_dataset['order_purchase_timestamp'].dt.date <= date_range[1]) &
    (main_dataset['product_category_name'].isin(selected_categories))
]

# Check if filtered data is empty
if filtered_data.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Main dashboard
st.title("🛍️ E-Commerce Analytics Dashboard")

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_data['price'].sum()
    st.metric("Total Sales", f"${total_sales:,.2f}")

with col2:
    avg_order_value = filtered_data['price'].mean()
    st.metric("Average Order Value", f"${avg_order_value:.2f}")

with col3:
    total_orders = filtered_data['product_id'].count()
    st.metric("Total Orders", f"{total_orders:,}")

with col4:
    unique_products = filtered_data['product_id'].nunique()
    st.metric("Unique Products", f"{unique_products:,}")

# Sales Trend
st.subheader("📈 Sales Trend Analysis")
daily_sales = filtered_data.groupby(
    filtered_data['order_purchase_timestamp'].dt.date
)['price'].sum().reset_index()

fig_trend = px.line(
    daily_sales,
    x='order_purchase_timestamp',
    y='price',
    title='Daily Sales Trend',
    template='plotly_white'
)
fig_trend.update_traces(line_color='#2E86C1')
fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Total Sales ($)",
    hovermode='x unified'
)
st.plotly_chart(fig_trend, use_container_width=True)

# Category Performance
st.subheader("📊 Category Performance")
col1, col2 = st.columns(2)

with col1:
    category_sales = (
        filtered_data.groupby('product_category_name')[['price']].sum()
        .sort_values('price', ascending=True)
        .tail(10)
    )
    fig_cat = px.bar(
        category_sales,
        orientation='h',
        title='Top 10 Categories by Sales',
        template='plotly_white'
    )
    fig_cat.update_traces(marker_color='#27AE60')
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    avg_category_price = (
        filtered_data.groupby('product_category_name')[['price']].mean()
        .sort_values('price', ascending=False)
        .head(10)
    )
    fig_avg = px.bar(
        avg_category_price,
        orientation='h',
        title='Top 10 Categories by Average Price',
        template='plotly_white'
    )
    fig_avg.update_traces(marker_color='#8E44AD')
    st.plotly_chart(fig_avg, use_container_width=True)

# Correlation Analysis
st.subheader("🔄 Price-Weight-Freight Correlation")
correlation_data = filtered_data[['price', 'freight_value', 'product_weight_g']].copy()
correlation_matrix = correlation_data.corr()

fig_corr = px.imshow(
    correlation_matrix,
    text_auto=True,
    aspect='auto',
    color_continuous_scale='RdBu',
    title='Correlation Heatmap'
)
st.plotly_chart(fig_corr, use_container_width=True)

# Download section
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Download Data")
if st.sidebar.button("Download Filtered Data as CSV"):
    csv = filtered_data.to_csv(index=False)
    st.sidebar.download_button(
        label="Click to Download",
        data=csv,
        file_name=f"ecommerce_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
