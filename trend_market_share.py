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

    # 1. Tren Market Share per Kategori
    st.subheader("📈 Trend Market Share (%) per Kategori Produk")
    fig1, ax1 = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=filtered_df, x="Tahun", y="Market Share (%)", hue="Kategori Produk", marker="o", style="Marketplace", ax=ax1)
    ax1.set_ylabel("Market Share (%)")
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Kategori Produk")
    plt.tight_layout()
    st.pyplot(fig1)

    # 2. Kontribusi Penjualan per Kategori & Marketplace
    st.subheader("💰 Kontribusi Penjualan (IDR) per Kategori dan Marketplace")
    penjualan_grouped = filtered_df.groupby(['Kategori Produk', 'Marketplace'])['Penjualan (IDR)'].sum().reset_index()
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=penjualan_grouped, x="Penjualan (IDR)", y="Kategori Produk", hue="Marketplace", ax=ax2)
    ax2.set_xlabel("Total Penjualan (IDR)")
    ax2.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"Rp{x:,.0f}"))
    ax2.set_ylabel("Kategori Produk")
    st.pyplot(fig2)

    st.markdown("**📦 Tabel Total Penjualan per Kategori & Marketplace**")
    penjualan_grouped['Penjualan (IDR)'] = penjualan_grouped['Penjualan (IDR)'].apply(lambda x: f"Rp{x:,.0f}")
    st.dataframe(penjualan_grouped, use_container_width=True)

    # 3. Gap Market Share Year-over-Year
    st.subheader("📉 Gap Market Share YoY per Kategori Produk")
    gap_df = filtered_df.groupby(['Kategori Produk', 'Tahun'])['Market Share (%)'].mean().unstack().diff(axis=1).dropna(axis=1)
    st.dataframe(gap_df.style.format("{:+.2f}%"), use_container_width=True)

    # 4. Donut Chart Market Share per Marketplace
    st.subheader("🥧 Distribusi Market Share per Marketplace")
    agg_market = filtered_df.groupby('Marketplace')['Market Share (%)'].sum()
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax3.pie(agg_market, labels=agg_market.index, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4))
    ax3.set_title("Total Market Share by Marketplace")
    ax3.axis('equal')
    st.pyplot(fig3)

    # 5. Pertumbuhan Penjualan YoY per Kategori
    st.subheader("📊 Pertumbuhan Penjualan YoY per Kategori Produk")
    yoy_df = filtered_df.groupby(['Kategori Produk', 'Tahun'])['Penjualan (IDR)'].sum().unstack()
    yoy_growth = yoy_df.pct_change(axis=1) * 100
    yoy_growth_display = yoy_growth.copy()
    yoy_growth_display.index.name = None
    yoy_growth_display.columns.name = "Tahun"
    st.dataframe(yoy_growth_display.style.format("{:+.2f}%"), use_container_width=True)

    # 6. Highlight Kategori dengan Market Share Tertinggi
    st.subheader("🏆 Kategori dengan Market Share Tertinggi (Tahun Terbaru)")
    tahun_terbaru = max(selected_tahun)
    latest_df = filtered_df[filtered_df['Tahun'] == tahun_terbaru]
    top_kategori = latest_df.groupby('Kategori Produk')['Market Share (%)'].mean().sort_values(ascending=False).reset_index()
    st.table(top_kategori.head(5).style.format({'Market Share (%)': "{:.2f}%"}))

    # Footer
    st.markdown("---")
    st.caption("📌 Data simulasi - bukan data aktual. Untuk keperluan analisis market share retail e-commerce Indonesia seperti Shopee, Tokopedia, TikTok Shop, dll.")
else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
