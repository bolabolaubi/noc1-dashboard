import streamlit as st
from datetime import datetime
import locale
import pandas as pd
from sheets_connector import append_ticket_safely, generate_ticket_number, connect_sheet
from email_generator import make_email

# 🌐 Atur locale bahasa Indonesia
try:
    locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID')
    except:
        locale.setlocale(locale.LC_TIME, 'ind')  # Fallback untuk Windows

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Anda harus login terlebih dahulu.")
    st.stop()
    
st.set_page_config(page_title="📝 Input Tiket Gangguan")
st.header("📝 Input Tiket Gangguan Baru")

# ✅ Ambil Spreadsheet ID dan Sheet Name
spreadsheet_id = st.session_state.get("spreadsheet_id")
sheet_name = st.session_state.get("sheet_name")

if not spreadsheet_id or not sheet_name:
    st.error("⚠️ Konfigurasi Spreadsheet belum diatur. Silakan buka halaman Admin terlebih dahulu.")
    st.stop()

# 🆔 Generate Nomor Tiket & Tanggal Hari Ini
ticket_id = generate_ticket_number(spreadsheet_id, sheet_name)
today_date = datetime.now().strftime("%d %B %Y")

# ============================
# 🔽 Ambil Data Master Dropdown
# ============================
def get_dropdown_list(sheet, key):
    try:
        records = connect_sheet(spreadsheet_id, sheet).get_all_records()
        return [row[key].strip() for row in records if row.get(key, "").strip()]
    except Exception as e:
        st.warning(f"Gagal mengambil data {key} dari {sheet}")
        return []

customer_list = get_dropdown_list("Data Customer", "Customer")
pic_list = get_dropdown_list("Data PIC", "PIC")

# ============================
# 📍 Input Lokasi dan Device
# ============================
selected_customer = st.selectbox("🏢 Customer", options=customer_list if customer_list else ["[Tidak ada data]"])
selected_lokasi = st.text_input("📍 Lokasi (Contoh: MKS-08_KCP Bone)")

device_input_raw = st.text_input("🔌 Device (pisahkan dengan koma)", placeholder="Contoh: MKS-08-1F-R1, MKS-08-1F-R2")
device_list = [d.strip().upper() for d in device_input_raw.split(",") if d.strip()]

# ============================
# 🔍 Deteksi Layanan dari Sheet
# ============================
def detect_layanan_from_device(devices):
    layanan_data = connect_sheet(spreadsheet_id, "Data Layanan").get_all_records()
    layanan_map = {
        row["Device"].strip().upper(): row["Layanan"]
        for row in layanan_data
        if "Device" in row and "Layanan" in row
    }

    hasil_layanan = []
    for dev in devices:
        kode_akhir = dev.strip().split("-")[-1].upper()
        layanan = layanan_map.get(kode_akhir, "Tidak diketahui")
        hasil_layanan.append(layanan)
    
    return hasil_layanan

# ============================
# 📝 Form Input Tiket
# ============================
with st.form("ticket_form"):
    waktu_down = st.text_input("⏰ Waktu Down Time", datetime.now().strftime('%H:%M'))
    insiden = st.selectbox("⚠️ Insiden", [" ", "RTO", "Down", "Loss", "High Latency", "Intermittent"])
    update_progres = st.text_area("🛠️ Update Progres")
    perbaikan = st.text_area("🔧 Perbaikan Gangguan")
    waktu_up = st.text_input("✅ Up Time", " ")
    status_layanan = st.text_input("📶 Status Layanan", " ")
    konfirm_pic = st.selectbox("👷 Konfirmasi PIC", options=pic_list if pic_list else ["[Tidak ada data]"])
    status_laporan = st.selectbox("📌 Status Laporan", ["Open", "On Going", "Close"])
    submitted = st.form_submit_button("✅ Submit Tiket")

# ============================
# 📤 Submit ke Spreadsheet
# ============================
if submitted:
    # 🔁 Proses ulang device & layanan setelah disubmit
    device_list = [d.strip().upper() for d in device_input_raw.split(",") if d.strip()]
    device_str = ", ".join(device_list)
    layanans = detect_layanan_from_device(device_list)
    layanan_str = " & ".join(layanans)

    ticket_data = {
        "No Ticket": ticket_id,
        "Tanggal": today_date,
        "Customer": selected_customer,
        "Lokasi": selected_lokasi,
        "Device": device_str,
        "Layanan": layanan_str,
        "Waktu Down Time": waktu_down,
        "Insiden": insiden,
        "Update Progres": update_progres,
        "Perbaikan Gangguan": perbaikan,
        "Up Time": waktu_up,
        "Status Layanan": status_layanan,
        "Konfirm PIC": konfirm_pic,
        "Status Laporan": status_laporan
    }

    append_ticket_safely(ticket_data, spreadsheet_id, sheet_name)
    st.success(f"✅ Tiket {ticket_id} berhasil disimpan ke Google Sheet!")

    st.subheader("📧 Email Template")
    email_body = make_email(ticket_data)
    st.text_area("📝 Email", value=email_body, height=300)