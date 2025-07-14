import streamlit as st
from datetime import datetime
import pandas as pd
from sheets_connector import get_ticket_by_id, update_ticket_by_id, connect_sheet

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Anda harus login terlebih dahulu.")
    st.stop()

st.set_page_config(page_title="✏️ Update Tiket")
st.header("✏️ Update Data Tiket")

# ✅ Ambil konfigurasi spreadsheet
spreadsheet_id = st.session_state.get("spreadsheet_id")
sheet_name = st.session_state.get("sheet_name")

if not spreadsheet_id or not sheet_name:
    st.error("⚠️ Konfigurasi Spreadsheet belum diatur. Silakan buka halaman Admin terlebih dahulu.")
    st.stop()

# ==============================
# 📥 Helper Dropdown Master Sheet
# ==============================
def get_dropdown_list(sheet, key):
    try:
        records = connect_sheet(spreadsheet_id, sheet).get_all_records()
        return [row[key].strip() for row in records if row.get(key, "").strip()]
    except:
        return []

customer_list = get_dropdown_list("Data Customer", "Customer")
pic_list = get_dropdown_list("Data PIC", "PIC")

# ==============================
# 🔍 Deteksi Layanan dari Sheet
# ==============================
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

# ==============================
# 🔎 Cari Tiket
# ==============================
with st.form("search_ticket_form"):
    ticket_id = st.text_input("🔎 Masukkan No Ticket untuk Dicari", value=st.session_state.get("last_search", ""))
    search = st.form_submit_button("Cari Ticket")

if search:
    ticket_data, row_index = get_ticket_by_id(ticket_id, spreadsheet_id, sheet_name)
    if ticket_data:
        st.session_state["ticket_data"] = ticket_data
        st.session_state["row_index"] = row_index
        st.session_state["last_search"] = ticket_id
        st.success(f"✅ Tiket {ticket_id} ditemukan di baris {row_index}")
    else:
        st.warning("❌ Tiket tidak ditemukan.")
        st.session_state.pop("ticket_data", None)

# ==============================
# ✏️ Form Update Tiket
# ==============================
if "ticket_data" in st.session_state:
    data = st.session_state["ticket_data"]

    with st.form("update_form"):
        tanggal = st.text_input("📅 Tanggal", data["Tanggal"])

        customer = st.selectbox(
            "👤 Customer",
            options=customer_list if customer_list else ["[Tidak ada data]"],
            index=customer_list.index(data["Customer"]) if data["Customer"] in customer_list else 0
        )

        lokasi = st.text_input("📍 Lokasi", data["Lokasi"])
        device = st.text_input("💻 Device", data["Device"])
        waktu_down = st.text_input("⏰ Waktu Down Time", data["Waktu Down Time"])
        insiden = st.text_input("⚠️ Insiden", data["Insiden"])
        progres = st.text_area("🛠️ Update Progres", data["Update Progres"])
        perbaikan = st.text_area("🔧 Perbaikan Gangguan", data["Perbaikan Gangguan"])
        waktu_up = st.text_input("✅ Up Time", data["Up Time"])
        status_layanan = st.text_input("📶 Status Layanan", data["Status Layanan"])

        pic = st.selectbox(
            "👷 Konfirmasi PIC",
            options=pic_list if pic_list else ["[Tidak ada data]"],
            index=pic_list.index(data["Konfirm PIC"]) if data["Konfirm PIC"] in pic_list else 0
        )

        status_laporan = st.selectbox(
            "📌 Status Laporan",
            ["Open", "On Going", "Close"],
            index=["Open", "On Going", "Close"].index(data["Status Laporan"])
        )

        # 🔍 Deteksi ulang layanan
        device_list = [d.strip().upper() for d in device.split(",") if d.strip()]
        layanans = detect_layanan_from_device(device_list)
        layanan = " & ".join(layanans)

        simpan = st.form_submit_button("💾 Simpan Perubahan")

        if simpan:
            new_data = {
                "No Ticket": st.session_state["last_search"].strip(),
                "Tanggal": tanggal,
                "Customer": customer,
                "Lokasi": lokasi,
                "Device": device.upper(),
                "Layanan": layanan,
                "Waktu Down Time": waktu_down,
                "Insiden": insiden,
                "Update Progres": progres,
                "Perbaikan Gangguan": perbaikan,
                "Up Time": waktu_up,
                "Status Layanan": status_layanan,
                "Konfirm PIC": pic,
                "Status Laporan": status_laporan
            }

            success = update_ticket_by_id(new_data["No Ticket"], new_data, spreadsheet_id, sheet_name)

            if success:
                st.success("✅ Tiket berhasil diperbarui!")
                for key in ["ticket_data", "row_index", "last_search"]:
                    st.session_state.pop(key, None)
                st.rerun()
            else:
                st.error("❌ Gagal memperbarui. Periksa kembali No Ticket.")