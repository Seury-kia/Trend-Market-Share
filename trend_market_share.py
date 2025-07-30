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
        df['Volume Sales (IDR)'] = df['Penjualan ( IDR )'].str.replace(',', '').astype(float)
        df.drop(columns=['Penjualan ( IDR )'], inplace=True)

    if 'Volume Unit' in df.columns:
        df['Qty Sales'] = df['Volume Unit'].str.replace(',', '').astype(float)
        df.drop(columns=['Volume Unit'], inplace=True)

    if 'Tahun' in df.columns:
        df['Tahun'] = df['Tahun'].astype(int)

    return df

df = load_data()

if df is not None and not df.empty:
    # Sidebar filters
    with st.sidebar:
        st.header("📌 Navigasi Data Berdasarkan:")
        sheet_tab = st.radio("Pilih Tampilan:", ["Tabel Gabungan", "Per Kategori Produk", "Per Marketplace", "Per Tahun"])

        st.markdown("---")
        st.header("🔍 Filter Data")
        selected_marketplace = st.multiselect("Pilih Marketplace", options=df['Marketplace'].unique(), default=df['Marketplace'].unique())
        selected_tahun = st.multiselect("Pilih Tahun", options=sorted(df['Tahun'].unique()), default=sorted(df['Tahun'].unique()))
        selected_kategori = st.multiselect("Pilih Kategori Produk", options=df['Kategori Produk'].unique(), default=df['Kategori Produk'].unique())

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & 
                     (df['Tahun'].isin(selected_tahun)) & 
                     (df['Kategori Produk'].isin(selected_kategori))]

    st.title("📊 Dashboard Trend Market Share Indonesia - Retail/FMCG")

    if sheet_tab == "Tabel Gabungan":
        df_2024_2025 = filtered_df[filtered_df['Tahun'].isin([2024, 2025])]

        combined_df = df_2024_2025.groupby(['Kategori Produk', 'Tahun']).agg({
            'Qty Sales': 'sum',
            'Volume Sales (IDR)': 'sum',
            'Market Share (%)': 'mean'
        }).reset_index()

        pivot_combined = combined_df.pivot(index='Kategori Produk', columns='Tahun')
        pivot_combined.columns = [f"{col[1]} {col[0]}" for col in pivot_combined.columns]
        pivot_combined.reset_index(inplace=True)

        for metric in ['Qty Sales', 'Volume Sales (IDR)', 'Market Share (%)']:
            if f"2024 {metric}" in pivot_combined.columns and f"2025 {metric}" in pivot_combined.columns:
                pivot_combined[f"Gap {metric}"] = pivot_combined[f"2025 {metric}"] - pivot_combined[f"2024 {metric}"]
                pivot_combined[f"Growth {metric}"] = ((pivot_combined[f"2025 {metric}"] - pivot_combined[f"2024 {metric}"]) / pivot_combined[f"2024 {metric}"]) * 100

        for col in pivot_combined.columns:
            if 'Volume Sales' in col:
                pivot_combined[col] = pivot_combined[col].apply(lambda x: f"Rp{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)
            elif 'Qty Sales' in col:
                pivot_combined[col] = pivot_combined[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)
            elif 'Market Share' in col:
                pivot_combined[col] = pivot_combined[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x)
            elif 'Growth' in col or 'Gap' in col:
                if 'Market Share' in col:
                    pivot_combined[col] = pivot_combined[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) and isinstance(x, (int, float)) else x)
                elif 'Volume Sales' in col:
                    pivot_combined[col] = pivot_combined[col].apply(lambda x: f"Rp{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)
                elif 'Qty Sales' in col:
                    pivot_combined[col] = pivot_combined[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else x)

        st.subheader("📋 Tabel Gabungan Qty, Volume, Market Share per Kategori Produk")
        st.dataframe(pivot_combined, use_container_width=True)

    elif sheet_tab == "Per Kategori Produk":
        st.subheader("📌 Data per Kategori Produk")
        st.dataframe(filtered_df.sort_values(by="Kategori Produk"), use_container_width=True)

    elif sheet_tab == "Per Marketplace":
        st.subheader("📌 Data per Marketplace")
        st.dataframe(filtered_df.sort_values(by="Marketplace"), use_container_width=True)

    elif sheet_tab == "Per Tahun":
        st.subheader("📌 Data per Tahun")
        st.dataframe(filtered_df.sort_values(by="Tahun"), use_container_width=True)

    st.caption("📌 Data simulasi - bukan data aktual. Untuk keperluan analisis market share retail e-commerce Indonesia seperti Shopee, Tokopedia, TikTok Shop, dll.")

else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
