import os
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for styling
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
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    df['product_category_name'] = df['product_category_name'].fillna('Unknown Category')
    
    numeric_columns = ['price', 'freight_value', 'product_weight_g']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())
    
    if 'quantity' not in df.columns:
        df['quantity'] = 1  
    return df

# Load dataset
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, 'main_dataset.csv')
main_dataset = load_data(dataset_path)

# Verify required columns
required_columns = ['order_purchase_timestamp', 'product_category_name', 'price', 'product_id', 'freight_value', 'product_weight_g', 'quantity']
missing_columns = [col for col in required_columns if col not in main_dataset.columns]
if missing_columns:
    st.error(f"Missing required columns in the dataset: {missing_columns}")
    st.stop()

# Sidebar filters
st.sidebar.title("📊 Dashboard Controls")
min_date = main_dataset['order_purchase_timestamp'].min().date()
max_date = main_dataset['order_purchase_timestamp'].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

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

if filtered_data.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Save filtered data for notebook analysis
if st.sidebar.button("Save Filtered Data for Notebook Analysis"):
    filtered_data.to_csv("filtered_data_for_notebook.csv", index=False)
    st.sidebar.success("Filtered data saved as 'filtered_data_for_notebook.csv'")

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
    total_orders = filtered_data['quantity'].sum()
    st.metric("Total Orders", f"{total_orders:,}")

with col4:
    unique_products = filtered_data['product_id'].nunique()
    st.metric("Unique Products", f"{unique_products:,}")

# Pertanyaan 1: Produk dengan Total Penjualan Tertinggi
st.subheader("🏆 Produk dengan Total Penjualan Tertinggi")

top_products = filtered_data.groupby(['product_id', 'product_category_name'])['price'].sum().nlargest(10).reset_index()

top_products_chart = px.bar(
    top_products,
    x='product_category_name',  
    y='price',
    title="Top 10 Produk dengan Total Penjualan Tertinggi",
    labels={'price': 'Total Penjualan ($)', 'product_category_name': 'Nama Produk'}, 
    template='plotly_white'
)

st.plotly_chart(top_products_chart, use_container_width=True)


# Pertanyaan 2: Pola Penjualan Berdasarkan Waktu
st.subheader("📆 Pola Penjualan Mingguan")
weekly_sales = filtered_data.set_index('order_purchase_timestamp').resample('W')['price'].sum().reset_index()
weekly_sales_chart = px.line(
    weekly_sales,
    x='order_purchase_timestamp',
    y='price',
    title='Tren Penjualan Mingguan',
    labels={'price': 'Total Penjualan ($)', 'order_purchase_timestamp': 'Tanggal'},
    template='plotly_white'
)
st.plotly_chart(weekly_sales_chart, use_container_width=True)

# Pertanyaan 3: Pengaruh Diskon atau Promosi terhadap Penjualan
st.subheader("🎯 Pengaruh Diskon/Promosi terhadap Penjualan")

filtered_data['discount'] = filtered_data['price'] - filtered_data['payment_value']

filtered_data['discount_status'] = filtered_data['discount'].apply(
    lambda x: 'Dengan Diskon' if x > 0 else 'Tanpa Diskon'
)

discount_impact = filtered_data.groupby('discount_status').agg({
    'price': 'sum',                # Total harga asli
    'payment_value': 'sum',        # Total pembayaran yang diterima
    'quantity': 'sum'              # Total kuantitas yang terjual
}).reset_index()

# Visualisasi Total Penjualan (Asli vs Pembayaran yang Diterima)
sales_comparison_chart = px.bar(
    discount_impact,
    x='discount_status',
    y=['price', 'payment_value'],
    title='Total Penjualan: Dengan vs Tanpa Diskon',
    labels={'value': 'Total Penjualan ($)', 'variable': 'Jenis Harga'},
    barmode='group',
    template='plotly_white'
)
st.plotly_chart(sales_comparison_chart, use_container_width=True)

# Insight
st.info(
    "Penawaran diskon atau promosi terbukti efektif dalam meningkatkan volume penjualan. "
    "Diskon memberikan insentif yang kuat bagi pelanggan untuk melakukan pembelian."
)

# Pertanyaan 4: Korelasi antara Harga dan Jumlah Penjualan
st.subheader("📉 Korelasi Harga Produk dan Jumlah Penjualan")
price_quantity_corr = filtered_data[['price', 'quantity']].corr().iloc[0, 1]
st.write(f"Koefisien Korelasi antara Harga dan Jumlah Penjualan: {price_quantity_corr:.2f}")
corr_scatter = px.scatter(
    filtered_data,
    x='price',
    y='quantity',
    title='Scatter Plot: Harga vs Jumlah Penjualan',
    labels={'price': 'Harga ($)', 'quantity': 'Jumlah Penjualan'},
    template='plotly_white'
)
st.plotly_chart(corr_scatter, use_container_width=True)
