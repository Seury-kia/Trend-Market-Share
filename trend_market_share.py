import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

# Set up layout
st.set_page_config(page_title="Dashboard Trend Market Share Indonesia", layout="wide")
sns.set(style="whitegrid")

# Load data from Google Sheet (published as CSV)
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1n9uo1ykNZqV_iNzvhg9MgKvQdTxzyaVDN_a49_hiN6g/export?format=csv"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    # Format & clean data
    if 'Market Share ( % )' in df.columns:
        df['Market Share (%)'] = df['Market Share ( % )'].str.replace('%', '').astype(float)
        df.drop(columns=['Market Share ( % )'], inplace=True)
    elif 'Market Share (%)' not in df.columns:
        st.error("Kolom 'Market Share ( % )' atau 'Market Share (%)' tidak ditemukan di data.")

    if 'Penjualan ( IDR )' in df.columns:
        df['Penjualan (IDR)'] = df['Penjualan ( IDR )'].str.replace(',', '').astype(float)
        df.drop(columns=['Penjualan ( IDR )'], inplace=True)

    if 'Volume Unit' in df.columns:
        df['Volume Unit'] = df['Volume Unit'].str.replace(',', '').astype(float)

    if 'Tahun' in df.columns:
        df['Tahun'] = df['Tahun'].astype(int)

    return df

df = load_data()

if df is not None and not df.empty:
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")
    selected_marketplace = st.sidebar.multiselect("Pilih Marketplace", options=df['Marketplace'].unique(), default=df['Marketplace'].unique())
    selected_tahun = st.sidebar.multiselect("Pilih Tahun", options=sorted(df['Tahun'].unique()), default=sorted(df['Tahun'].unique()))
    selected_kategori = st.sidebar.multiselect("Pilih Kategori Produk", options=df['Kategori Produk'].unique(), default=df['Kategori Produk'].unique())

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & 
                     (df['Tahun'].isin(selected_tahun)) & 
                     (df['Kategori Produk'].isin(selected_kategori))]

    # Title
    st.title("📊 Dashboard Trend Market Share Indonesia - Retail/FMCG")

    # 1. Tabel Detail Market Share per Kategori Tahun 2024 & 2025
    st.subheader("📊 Tabel Data per Kategori - Tahun 2024 & 2025")
    df_2024_2025 = filtered_df[filtered_df['Tahun'].isin([2024, 2025])]
    if not df_2024_2025.empty:
        table_df = df_2024_2025.groupby(['Kategori Produk', 'Tahun']).agg({
            'Market Share (%)': 'mean',
            'Penjualan (IDR)': 'sum',
            'Volume Unit': 'sum'
        }).reset_index()

        table_df = table_df.sort_values(by=['Kategori Produk', 'Tahun'])
        table_df['Market Share (%)'] = table_df['Market Share (%)'].round(2)
        table_df['Penjualan (IDR)'] = table_df['Penjualan (IDR)'].apply(lambda x: f"Rp{x:,.0f}")
        table_df['Volume Unit'] = table_df['Volume Unit'].apply(lambda x: f"{x:,.0f}")

        st.dataframe(table_df, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption("📌 Data simulasi - bukan data aktual. Untuk keperluan analisis market share retail e-commerce Indonesia seperti Shopee, Tokopedia, TikTok Shop, dll.")
else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
