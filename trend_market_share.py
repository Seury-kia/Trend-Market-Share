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
        st.header("\U0001F4CC Navigasi Data Berdasarkan:")
        sheet_tab = st.radio("Pilih Tampilan:", ["Performance Detail", "Per Kategori Produk", "Per Marketplace", "Per Tahun"])

        st.markdown("---")
        st.header("\U0001F50D Filter Data")

        marketplace_list = df['Marketplace'].unique().tolist()
        tahun_list = sorted(df['Tahun'].unique().tolist())
        kategori_list = df['Kategori Produk'].unique().tolist()

        selected_marketplace = st.multiselect("Pilih Marketplace", options=['All'] + marketplace_list, default=['All'])
        selected_tahun = st.multiselect("Pilih Tahun", options=['All'] + tahun_list, default=['All'])
        selected_kategori = st.multiselect("Pilih Kategori Produk", options=['All'] + kategori_list, default=['All'])

        if 'All' in selected_marketplace:
            selected_marketplace = marketplace_list
        if 'All' in selected_tahun:
            selected_tahun = tahun_list
        if 'All' in selected_kategori:
            selected_kategori = kategori_list

        st.markdown("---")
        st.header("\U0001F4DD Pilih Jenis Data")
        selected_metrics = st.multiselect(
            "Tampilkan metrik:",
            options=["Market Share (%)", "Volume Sales (IDR)", "Qty Sales"],
            default=["Market Share (%)"]
        )

    filtered_df = df[(df['Marketplace'].isin(selected_marketplace)) & 
                     (df['Tahun'].isin(selected_tahun)) & 
                     (df['Kategori Produk'].isin(selected_kategori))]

    st.title("\U0001F4CA Dashboard Trend Market Share Indonesia - Retail/FMCG")

    if sheet_tab == "Performance Detail":
        df_2024_2025 = filtered_df[filtered_df['Tahun'].isin([2024, 2025])]

        tampilan_ringkas = st.toggle("Tampilkan versi ringkas (Mobile Friendly)", value=False)

        for metric, label, is_percent, is_currency in [
            ('Market Share (%)', 'Market Share (%)', True, False),
            ('Volume Sales (IDR)', 'Volume Sales (IDR)', False, True),
            ('Qty Sales', 'Qty Sales', False, False)
        ]:
            if label not in selected_metrics:
                continue

            grouped = df_2024_2025.groupby(['Kategori Produk', 'Tahun'])[metric].sum().reset_index()
            pivot = grouped.pivot(index='Kategori Produk', columns='Tahun', values=metric).reset_index()

            pivot['Gap'] = pivot.get(2025, 0) - pivot.get(2024, 0)
            pivot['Growth'] = ((pivot.get(2025, 0) - pivot.get(2024, 0)) / pivot.get(2024, 1)) * 100
            pivot[['Gap', 'Growth']] = pivot[['Gap', 'Growth']].fillna(0)

            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                sort_column = st.selectbox(f"Urutkan {label} berdasarkan:", options=[2024, 2025, 'Gap', 'Growth'], key=label)
            with col2:
                sort_mode = st.radio(f"Urutan Data", ["Largest", "Smallest"], horizontal=True, key=label+"_mode")
            with col3:
                sort_topflop = st.radio(f"", ["All", "Top", "Flop"], horizontal=True, key=label+"_order")

            ascending_mode = sort_mode == "Smallest"
            if sort_column in pivot.columns:
                pivot = pivot.sort_values(by=sort_column, ascending=ascending_mode)
            else:
                st.warning(f"Kolom '{sort_column}' tidak tersedia dalam data.")

            if sort_topflop == "Top":
                pivot = pivot.head(10)
            elif sort_topflop == "Flop":
                pivot = pivot.tail(10)

            pivot_display = pivot.copy()

            for col in pivot_display.columns:
                if col != "Kategori Produk":
                    if is_percent and col in [2024, 2025, 'Gap', 'Growth']:
                        pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
                    elif is_currency and col in [2024, 2025, 'Gap']:
                        pivot_display[col] = pivot_display[col].apply(lambda x: f"Rp{x:,.0f}" if pd.notnull(x) else "")
                    elif col == 'Growth':
                        pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")
                    else:
                        pivot_display[col] = pivot_display[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")

            st.subheader(f"\U0001F4CB {label} per Kategori Produk")
            st.caption(f"Menampilkan {sort_topflop} berdasarkan kolom '{sort_column}' dalam mode '{sort_mode}'")
            st.markdown("*Geser tabel ke kanan untuk melihat data selengkapnya →*")

            if not pivot.empty:
                if tampilan_ringkas:
                    ringkas_cols = [col for col in pivot_display.columns if col in ['Kategori Produk', 2025, 'Growth']]
                    st.dataframe(pivot_display[ringkas_cols], use_container_width=True, hide_index=True)
                else:
                    st.dataframe(pivot_display, use_container_width=True, hide_index=True)

                if sort_topflop in ["Top", "Flop"]:
                    st.subheader(f"\U0001F4C8 Grafik {label} - {'Top 10' if sort_topflop == 'Top' else 'Flop 10'}")
                    fig, ax1 = plt.subplots(figsize=(12, 6))

                    kategori = pivot['Kategori Produk']
                    x = range(len(kategori))
                    width = 0.25

                    ax1.bar([i - width for i in x], pivot[2024], width=width, label='2024')
                    ax1.bar(x, pivot[2025], width=width, label='2025')
                    ax1.bar([i + width for i in x], pivot['Gap'], width=width, label='Gap')
                    ax1.set_ylabel(label)
                    ax1.set_xticks(x)
                    ax1.set_xticklabels(kategori, rotation=45, ha='right')
                    ax1.legend(loc='upper center', ncol=4)
                    ax1.grid(False)

                    ax2 = ax1.twinx()
                    ax2.plot(x, pivot['Growth'], color='red', marker='o', label='Growth (%)')
                    ax2.set_ylabel("Growth (%)")
                    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
                    ax2.grid(False)

                    fig.tight_layout()
                    st.pyplot(fig)
                else:
                    st.subheader("")
            else:
                st.warning("Data kosong setelah filter diterapkan.")

    elif sheet_tab == "Per Kategori Produk":
        st.subheader("\U0001F4CC Data per Kategori Produk")
        st.dataframe(filtered_df.sort_values(by="Kategori Produk"), use_container_width=True, hide_index=True)

    elif sheet_tab == "Per Marketplace":
        st.subheader("\U0001F4CC Data per Marketplace")
        st.dataframe(filtered_df.sort_values(by="Marketplace"), use_container_width=True, hide_index=True)

    elif sheet_tab == "Per Tahun":
        st.subheader("\U0001F4CC Data per Tahun")
        st.dataframe(filtered_df.sort_values(by="Tahun"), use_container_width=True, hide_index=True)

    st.caption("\U0001F4CC Data simulasi - bukan data aktual. Untuk keperluan analisis market share retail e-commerce Indonesia seperti Shopee, Tokopedia, TikTok Shop, dll.")

else:
    st.warning("Data tidak berhasil dimuat atau kosong. Periksa kembali format Google Sheet.")
