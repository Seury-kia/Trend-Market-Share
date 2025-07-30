import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up layout
st.set_page_config(page_title="Dashboard Trend Market Share Indonesia", layout="wide")
sns.set(style="whitegrid")

# Load data from Google Sheet (published as CSV)
@st.cache_data

def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1n9uo1ykNZqV_iNzvhg9MgKvQdTxzyaVDN_a49_hiN6g/export?format=csv"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()

    # Debug kolom
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
    st.sidebar.header("Filter Data")
    selected_marketplace = st.sidebar.multiselect("Pilih Marketplace", options=df['Marketplace'].unique(), default=df['Marketplace'].unique())
    selected_tahun = st.sidebar.multiselect("Pilih Tahun", options=sorted(df['Tahun'].unique()), default=sorted(df['Tahun'].unique()))

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & (df['Tahun'].isin(selected_tahun))]

    # Title
    st.title("📊 Dashboard Trend Market Share Indonesia - Retail/FMCG")

    # 1. Tren Market Share per Kategori
    st.subheader("Trend Market Share (%) per Kategori Produk")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=filtered_df, x="Tahun", y="Market Share (%)", hue="Kategori Produk", marker="o", style="Marketplace", ax=ax1)
    ax1.set_ylabel("Market Share (%)")
    st.pyplot(fig1)

    # 2. Kontribusi Kategori per Marketplace
    st.subheader("Kontribusi Penjualan (IDR) per Kategori dan Marketplace")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=filtered_df, x="Penjualan (IDR)", y="Kategori Produk", hue="Marketplace", estimator=sum, ci=None, ax=ax2)
    ax2.set_xlabel("Total Penjualan (IDR)")
    st.pyplot(fig2)

    # 3. Gap Market Share Year-over-Year
    st.subheader("Gap Market Share YoY per Kategori Produk")
    gap_df = filtered_df.groupby(['Kategori Produk', 'Tahun'])['Market Share (%)'].mean().unstack().diff(axis=1).dropna(axis=1)
    st.dataframe(gap_df, use_container_width=True)

    # 4. Donut Chart Kontribusi Total per Marketplace
    st.subheader("Distribusi Market Share per Marketplace")
    agg_market = filtered_df.groupby('Marketplace')['Market Share (%)'].sum()
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax3.pie(agg_market, labels=agg_market.index, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4))
    ax3.axis('equal')
    st.pyplot(fig3)

    # Footer
    st.markdown("---")
    st.caption("Data bersifat dummy untuk simulasi analisis pasar retail Indonesia (Shopee, Tokopedia, TikTok Shop, dll)")
else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
