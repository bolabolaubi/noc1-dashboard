import streamlit as st
import pandas as pd
import numpy as np
from sheets_connector import connect_sheet
import plotly.express as px
import dateparser

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Anda harus login terlebih dahulu.")
    st.stop()

st.set_page_config(page_title="📊 Dashboard", layout="wide")
st.title("📊 Dashboard Laporan Tiket Gangguan")

# ============================ #
# 🛠️ SIDEBAR: Konfigurasi Admin
# ============================ #
st.sidebar.markdown("## ⚙️ Konfigurasi Spreadsheet")

# Set default jika belum ada
if "spreadsheet_id" not in st.session_state:
    st.session_state["spreadsheet_id"] = "Laporan_Ticket_Gangguan_Dummy"
if "sheet_name" not in st.session_state:
    st.session_state["sheet_name"] = "Open_Ticket"

# Input form di sidebar
spreadsheet_id = st.sidebar.text_input("📄 Spreadsheet ID", value=st.session_state["spreadsheet_id"])
sheet_name = st.sidebar.text_input("🗂️ Sheet Name", value=st.session_state["sheet_name"])

# Tombol Simpan
if st.sidebar.button("🔁 Terapkan Spreadsheet Baru"):
    st.session_state["spreadsheet_id"] = spreadsheet_id
    st.session_state["sheet_name"] = sheet_name
    st.success("✅ Konfigurasi diperbarui!")

# 🔌 Koneksi ke Sheet
sheet = connect_sheet(st.session_state["spreadsheet_id"], st.session_state["sheet_name"])

# ============================ #
# 📥 Ambil dan Proses Data
# ============================ #
data = pd.DataFrame(sheet.get_all_records())

# 🧼 Format kolom Tanggal
data["Tanggal"] = data["Tanggal"].apply(lambda x: dateparser.parse(str(x)))

# 🧼 Kolom numerik
numeric_cols = ["Up Time"]
for col in numeric_cols:
    if col in data.columns:
        # Bersihkan nilai kosong dan teks None
        data[col] = data[col].replace([" ", "None", None], np.nan)
        
        # Konversi ke numerik
        data[col] = pd.to_numeric(data[col], errors="coerce")
        
        # Jika mau, bisa isi NaN dengan 0
        data[col] = data[col].fillna(0)

# 🧾 Tambahkan kolom Bulan dan Tahun
data["Tahun"] = data["Tanggal"].dt.year
data["Bulan"] = data["Tanggal"].dt.strftime("%B")  # ex: "Juli"

# ============================ #
# 🔍 Sidebar Filter Data
# ============================ #
st.sidebar.markdown("## 🔎 Filter Data")

status_filter = st.sidebar.multiselect(
    "Status Laporan",
    options=data["Status Laporan"].dropna().unique(),
    default=data["Status Laporan"].dropna().unique()
)

tahun_filter = st.sidebar.selectbox("Tahun", sorted(data["Tahun"].dropna().unique(), reverse=True))
bulan_filter = st.sidebar.selectbox("Bulan", pd.date_range("2023-01-01", "2025-12-01", freq="MS").strftime("%B").unique())

# Terapkan filter
filtered_data = data[
    (data["Status Laporan"].isin(status_filter)) &
    (data["Tahun"] == tahun_filter) &
    (data["Bulan"] == bulan_filter)
]

# ============================ #
# 📋 Tampilkan Data & Statistik
# ============================ #
st.subheader("📑 Data Tiket")
st.dataframe(filtered_data, use_container_width=True)

st.subheader("📈 Ringkasan Statistik")
col1, col2, col3 = st.columns(3)
col1.metric("Total Tiket", len(filtered_data))
col2.metric("Status On Going", (filtered_data["Status Laporan"] == "On Going").sum())
col3.metric("Status Close", (filtered_data["Status Laporan"] == "Close").sum())

# ============================ #
# 📊 Visualisasi Lokasi
# ============================ #
st.subheader("📍 Jumlah Tiket per Lokasi (Filtered)")
if not filtered_data.empty:
    fig = px.bar(
        filtered_data.groupby("Lokasi").size().reset_index(name="Jumlah Tiket"),
        x="Lokasi",
        y="Jumlah Tiket",
        title=f"Tiket di Bulan {bulan_filter} {tahun_filter}",
        labels={"Jumlah Tiket": "Jumlah Tiket", "Lokasi": "Lokasi"},
        color="Jumlah Tiket",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tidak ada data untuk filter yang dipilih.")


if st.sidebar.button("🔒 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()