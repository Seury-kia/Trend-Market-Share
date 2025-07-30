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
        sheet_tab = st.radio("Pilih Tampilan:", ["Keseluruhan", "Per Kategori", "Per Marketplace", "Per Tahun"])

        st.markdown("---")
        st.header("🔍 Filter Data")
        selected_marketplace = st.multiselect("Pilih Marketplace", options=df['Marketplace'].unique(), default=df['Marketplace'].unique())
        selected_tahun = st.multiselect("Pilih Tahun", options=sorted(df['Tahun'].unique()), default=sorted(df['Tahun'].unique()))
        selected_kategori = st.multiselect("Pilih Kategori Produk", options=df['Kategori Produk'].unique(), default=df['Kategori Produk'].unique())

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & 
                     (df['Tahun'].isin(selected_tahun)) & 
                     (df['Kategori Produk'].isin(selected_kategori))]

    st.title("📊 Dashboard Trend Market Share Indonesia - Retail/FMCG")

    df_2024_2025 = filtered_df[filtered_df['Tahun'].isin([2024, 2025])]

    sort_by_year = st.radio("Tahun yang dijadikan acuan pengurutan:", ["2024", "2025"], horizontal=True)
    sort_by_year = int(sort_by_year)

    def prepare_table(metric, subset_df=None):
        data = subset_df if subset_df is not None else df_2024_2025
        pivot_df = data.pivot_table(
            index='Kategori Produk', 
            columns='Tahun', 
            values=metric, 
            aggfunc='sum' if metric != 'Market Share (%)' else 'mean'
        ).reset_index()

        if 2024 in pivot_df.columns and 2025 in pivot_df.columns:
            pivot_df['Growth (%)'] = ((pivot_df[2025] - pivot_df[2024]) / pivot_df[2024]) * 100
            pivot_df['Gap'] = pivot_df[2025] - pivot_df[2024]

        pivot_df['Total Sort Value'] = pivot_df[sort_by_year] if sort_by_year in pivot_df.columns else 0

        pivot_df.rename(columns={2024: '2024', 2025: '2025'}, inplace=True)

        if metric == 'Volume Sales (IDR)':
            pivot_df['2024_raw'] = pivot_df['2024']
            pivot_df['2025_raw'] = pivot_df['2025']
            pivot_df['Gap_raw'] = pivot_df['Gap']
            pivot_df['2024'] = pivot_df['2024'].apply(lambda x: f"Rp{x:,.0f}")
            pivot_df['2025'] = pivot_df['2025'].apply(lambda x: f"Rp{x:,.0f}")
            pivot_df['Gap'] = pivot_df['Gap'].apply(lambda x: f"Rp{x:,.0f}")
        elif metric == 'Qty Sales':
            pivot_df['2024_raw'] = pivot_df['2024']
            pivot_df['2025_raw'] = pivot_df['2025']
            pivot_df['Gap_raw'] = pivot_df['Gap']
            pivot_df['2024'] = pivot_df['2024'].apply(lambda x: f"{x:,.0f}")
            pivot_df['2025'] = pivot_df['2025'].apply(lambda x: f"{x:,.0f}")
            pivot_df['Gap'] = pivot_df['Gap'].apply(lambda x: f"{x:,.0f}")
        elif metric == 'Market Share (%)':
            pivot_df['2024'] = pivot_df['2024'].round(2).astype(str) + '%'
            pivot_df['2025'] = pivot_df['2025'].round(2).astype(str) + '%'
            pivot_df['Gap'] = pivot_df['Gap'].round(2).astype(str) + '%'

        pivot_df['Growth_raw'] = pivot_df['Growth (%)']
        pivot_df['Growth (%)'] = pivot_df['Growth (%)'].round(2).astype(str) + '%'

        return pivot_df

    def style_growth(val):
        try:
            val_float = float(val.replace('%', ''))
            color = 'green' if val_float > 0 else 'red'
            return f'color: {color}'
        except:
            return ''

    def style_gap(val):
        try:
            if isinstance(val, str) and '%' in val:
                val_num = float(val.replace('%', ''))
            else:
                val_num = float(str(val).replace('Rp', '').replace(',', '').replace('.', ''))
            color = 'green' if val_num > 0 else 'red'
            return f'color: {color}'
        except:
            return ''

    def sort_table(df, order='desc', metric='Volume Sales (IDR)'):
        if metric == 'Market Share (%)':
            sort_col = str(sort_by_year).replace('%', '')
        else:
            sort_col = f"{sort_by_year}_raw"

        if sort_col not in df.columns:
            st.warning(f"⚠️ Kolom untuk sorting '{sort_col}' tidak ditemukan.")
            return df.style.set_properties(**{'font-size': '13px'})

        sorted_df = df.sort_values(by=sort_col, ascending=(order == 'asc'))
        drop_cols = ['Total Sort Value'] + [col for col in sorted_df.columns if '_raw' in col and col in sorted_df.columns]
        styled_df = sorted_df.drop(columns=drop_cols, errors='ignore')
        styled_df = styled_df.style.set_properties(**{
            'font-size': '12px',
            'text-align': 'left'
        }).applymap(style_growth, subset=['Growth (%)']).applymap(style_gap, subset=['Gap'])
        return styled_df

    if sheet_tab == "Keseluruhan":
        st.subheader("📊 Tabel Ringkasan Keseluruhan")
        st.subheader("📈 Market Share (%)")
        sort_order_ms = st.selectbox("Urutkan Market Share berdasarkan:", ["Large to Small", "Small to Large"], key="ms_sort")
        df_ms = prepare_table('Market Share (%)')
        st.write(sort_table(df_ms, order='desc' if sort_order_ms == "Large to Small" else 'asc', metric='Market Share (%)'))

        st.subheader("💰 Volume Sales (IDR)")
        sort_order_vs = st.selectbox("Urutkan Volume Sales berdasarkan:", ["Large to Small", "Small to Large"], key="vs_sort")
        df_vs = prepare_table('Volume Sales (IDR)')
        st.write(sort_table(df_vs, order='desc' if sort_order_vs == "Large to Small" else 'asc'))

        st.subheader("📦 Qty Sales")
        sort_order_qs = st.selectbox("Urutkan Qty Sales berdasarkan:", ["Large to Small", "Small to Large"], key="qs_sort")
        df_qs = prepare_table('Qty Sales')
        st.write(sort_table(df_qs, order='desc' if sort_order_qs == "Large to Small" else 'asc'))

    elif sheet_tab == "Per Kategori":
        st.subheader("📚 Sheet Berdasarkan Kategori Produk")
        for kategori in sorted(filtered_df['Kategori Produk'].unique()):
            st.markdown(f"### 🗂️ Kategori: {kategori}")
            subset = filtered_df[filtered_df['Kategori Produk'] == kategori]
            st.write("Market Share:")
            st.dataframe(prepare_table("Market Share (%)", subset))
            st.write("Volume Sales:")
            st.dataframe(prepare_table("Volume Sales (IDR)", subset))
            st.write("Qty Sales:")
            st.dataframe(prepare_table("Qty Sales", subset))
            st.markdown("---")

    elif sheet_tab == "Per Marketplace":
        st.subheader("📚 Sheet Berdasarkan Marketplace")
        for mp in sorted(filtered_df['Marketplace'].unique()):
            st.markdown(f"### 🛒 Marketplace: {mp}")
            subset = filtered_df[filtered_df['Marketplace'] == mp]
            st.write("Market Share:")
            st.dataframe(prepare_table("Market Share (%)", subset))
            st.write("Volume Sales:")
            st.dataframe(prepare_table("Volume Sales (IDR)", subset))
            st.write("Qty Sales:")
            st.dataframe(prepare_table("Qty Sales", subset))
            st.markdown("---")

    elif sheet_tab == "Per Tahun":
        st.subheader("📚 Sheet Berdasarkan Tahun")
        for thn in sorted(filtered_df['Tahun'].unique()):
            st.markdown(f"### 📅 Tahun: {thn}")
            subset = filtered_df[filtered_df['Tahun'] == thn]
            st.write("Market Share:")
            st.dataframe(prepare_table("Market Share (%)", subset))
            st.write("Volume Sales:")
            st.dataframe(prepare_table("Volume Sales (IDR)", subset))
            st.write("Qty Sales:")
            st.dataframe(prepare_table("Qty Sales", subset))
            st.markdown("---")

    st.caption("📌 Data simulasi - bukan data aktual. Untuk keperluan analisis market share retail e-commerce Indonesia seperti Shopee, Tokopedia, TikTok Shop, dll.")

else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
