import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

st.set_page_config(page_title="Trend Market Share FMCG", layout="wide")
st.title("📊 Dashboard Trend Market Share - FMCG Indonesia")

# --- Upload atau input link Google Sheet
st.sidebar.header("🔗 Data Source")
sheet_url = st.sidebar.text_input("Masukkan Link Google Sheet (format CSV):")

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

if sheet_url:
    try:
        df = load_data(sheet_url)

        # Format DataFrame
        df['Tahun'] = df['Tahun'].astype(int)
        kategori = df['Kategori'].unique()

        st.subheader("1️⃣ Tabel Market Share & Gap")
        pivot_df = df.pivot(index='Kategori', columns='Tahun', values='Market Share (%)').reset_index()
        pivot_df['Gap (%)'] = pivot_df[2024] - pivot_df[2023]
        pivot_df['Kontribusi 2024 (%)'] = pivot_df[2024]

        st.dataframe(pivot_df.style.format({
            2023: "{:.1f}%",
            2024: "{:.1f}%",
            "Gap (%)": "{:+.1f}%",
            "Kontribusi 2024 (%)": "{:.1f}%"
        }), use_container_width=True)

        # Pie Chart - Komposisi Market Share
        st.subheader("2️⃣ Komposisi Market Share 2024")
        fig1, ax1 = plt.subplots()
        ax1.pie(pivot_df['Kontribusi 2024 (%)'], labels=pivot_df['Kategori'], autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

        # Bar Chart - Gap Market Share
        st.subheader("3️⃣ GAP Market Share 2024 vs 2023")
        fig2, ax2 = plt.subplots()
        sns.barplot(data=pivot_df, y='Kategori', x='Gap (%)', ax=ax2, palette='coolwarm')
        ax2.axvline(0, color='gray', linestyle='--')
        st.pyplot(fig2)

        # Line Chart (Optional): Trend Bulanan (jika tersedia)
        if 'Bulan' in df.columns:
            st.subheader("4️⃣ Trend Bulanan Market Share")
            line_df = df.pivot_table(index='Bulan', columns='Kategori', values='Market Share (%)')
            st.line_chart(line_df)

    except Exception as e:
        st.error(f"⚠️ Gagal memuat data: {e}")
else:
    st.info("📥 Masukkan link Google Sheet CSV untuk memulai analisis.")