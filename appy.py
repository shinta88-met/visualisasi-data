import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==== CONFIGURASI DASHBOARD ====
st.set_page_config(page_title="Dashboard Pos Hujan Sumatera Selatan", layout="wide")
st.title("📈 Dashboard Interaktif Curah Hujan")
st.markdown("**UAS SHINTA MEDIANY_M8TB_14.24.0012**")

# ==== CEK FILE DI ROOT ====
DATA_PATH = Path("17 pos hujan.xlsx")

if not DATA_PATH.exists():
    st.error("❌ File Excel tidak ditemukan. Pastikan `17 pos hujan.xlsx` berada di folder utama (root).")
    st.stop()

# ==== LOAD FILE ====
xls = pd.ExcelFile(DATA_PATH)

# Sheet metadata lokasi
df_meta = xls.parse("pos hujan")
df_meta.columns = df_meta.columns.str.strip()
station_names = df_meta["Pos Hujan Kerja Sama"].str.replace("Pos hujan ", "").str.strip().tolist()

# ==== PILIH STASIUN ====
station = st.selectbox("📍 Pilih Pos Hujan", station_names)

# ==== FUNGSI LOAD DATA ====
def load_station_data(sheet_name):
    df = xls.parse(sheet_name)
    df.columns = df.columns.str.strip()
    
    date_col = [col for col in df.columns if "tanggal" in col.lower()]
    rain_col = [col for col in df.columns if "hujan" in col.lower()]
    if not date_col or not rain_col:
        return None

    df = df[[date_col[0], rain_col[0]]].dropna()
    df.columns = ["Tanggal", "Hujan"]
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors='coerce')
    df["Hujan"] = pd.to_numeric(df["Hujan"], errors='coerce')
    df = df.dropna(subset=["Tanggal"])
    return df

df = load_station_data(station)

if df is None or df.empty:
    st.warning("❗ Data tidak tersedia atau format salah untuk stasiun ini.")
    st.stop()

# ==== PROSES DATA ====
df["Bulan"] = df["Tanggal"].dt.to_period("M")
df["Tahun"] = df["Tanggal"].dt.year
bulanan = df.groupby("Bulan")["Hujan"].sum()
tahunan = df.groupby("Tahun")["Hujan"].sum()

# ==== VISUALISASI ====
tab1, tab2 = st.tabs(["📆 Tren Bulanan", "📅 Tren Tahunan"])

with tab1:
    st.subheader(f"📆 Curah Hujan Bulanan – {station}")
    fig, ax = plt.subplots(figsize=(12, 5))
    bulanan.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_ylabel("Curah Hujan (mm)")
    ax.set_xlabel("Bulan")
    ax.set_title("Total Curah Hujan Bulanan")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

with tab2:
    st.subheader(f"📅 Curah Hujan Tahunan – {station}")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    tahunan.plot(kind="bar", ax=ax2, color="orange")
    ax2.set_ylabel("Curah Hujan (mm)")
    ax2.set_xlabel("Tahun")
    ax2.set_title("Total Curah Hujan Tahunan")
    ax2.tick_params(axis='x', rotation=0)
    st.pyplot(fig2)

st.info(f"📄 Jumlah data tersedia: {len(df)} entri dari pos hujan **{station}**.")
