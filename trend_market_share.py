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
        sheet_tab = st.radio("Pilih Tampilan:", ["Performance Detail", "Per Kategori Produk", "Per Marketplace", "Per Tahun"])

        st.markdown("---")
        st.header("🔍 Filter Data")
        selected_marketplace = st.multiselect("Pilih Marketplace", options=df['Marketplace'].unique(), default=df['Marketplace'].unique())
        selected_tahun = st.multiselect("Pilih Tahun", options=sorted(df['Tahun'].unique()), default=sorted(df['Tahun'].unique()))
        selected_kategori = st.multiselect("Pilih Kategori Produk", options=df['Kategori Produk'].unique(), default=df['Kategori Produk'].unique())

        st.markdown("---")
        sort_order = st.radio("Urutkan berdasarkan total 2024 + 2025", ["Largest to Smallest", "Smallest to Largest"], index=0)
        ascending_sort = sort_order == "Smallest to Largest"

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & 
                     (df['Tahun'].isin(selected_tahun)) & 
                     (df['Kategori Produk'].isin(selected_kategori))]

    st.title("📊 Dashboard Trend Market Share Indonesia - Retail/FMCG")

    if sheet_tab == "Performance Detail":
        df_2024_2025 = filtered_df[filtered_df['Tahun'].isin([2024, 2025])]

        for metric, label, is_percent, is_currency in [
            ('Market Share (%)', 'Market Share (%)', True, False),
            ('Volume Sales (IDR)', 'Volume Sales (IDR)', False, True),
            ('Qty Sales', 'Qty Sales', False, False)
        ]:
            grouped = df_2024_2025.groupby(['Kategori Produk', 'Tahun'])[metric].sum().reset_index()
            pivot = grouped.pivot(index='Kategori Produk', columns='Tahun', values=metric).reset_index()
            pivot['Gap'] = pivot[2025] - pivot[2024]
            pivot['Growth'] = ((pivot[2025] - pivot[2024]) / pivot[2024]) * 100

            pivot['Total'] = pivot[2024] + pivot[2025]
            pivot = pivot.sort_values(by='Total', ascending=ascending_sort)

            if is_percent:
                for year in [2024, 2025]:
                    pivot[year] = pivot[year].apply(lambda x: f"{x:.2f}%")
                pivot['Gap'] = pivot['Gap'].apply(lambda x: f"{x:.2f}%")
                pivot['Growth'] = pivot['Growth'].apply(lambda x: f"{x:.2f}%")
            elif is_currency:
                for year in [2024, 2025]:
                    pivot[year] = pivot[year].apply(lambda x: f"Rp{x:,.0f}")
                pivot['Gap'] = pivot['Gap'].apply(lambda x: f"Rp{x:,.0f}")
                pivot['Growth'] = pivot['Growth'].apply(lambda x: f"{x:.2f}%")
            else:
                for year in [2024, 2025]:
                    pivot[year] = pivot[year].apply(lambda x: f"{x:,.0f}")
                pivot['Gap'] = pivot['Gap'].apply(lambda x: f"{x:,.0f}")
                pivot['Growth'] = pivot['Growth'].apply(lambda x: f"{x:.2f}%")

            st.subheader(f"📋 {label} per Kategori Produk")
            st.dataframe(pivot.drop(columns=['Total']), use_container_width=True)

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
