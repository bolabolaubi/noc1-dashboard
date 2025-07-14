import streamlit as st
from datetime import datetime
import gspread
from google.oauth2 import service_account

# 🔌 Koneksi ke Google Sheet
def connect_sheet(spreadsheet_id, sheet_name):
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# 🆔 Generate Nomor Tiket Otomatis
def generate_ticket_number(spreadsheet_id, sheet_name):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    records = sheet.get_all_records()
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"TT{today_str}"
    nomor_urut_tertinggi = 0

    for row in records:
        ticket = row.get("No Ticket", "").strip()
        if ticket.startswith(prefix):
            try:
                no_urut = int(ticket.replace(prefix, ""))
                nomor_urut_tertinggi = max(nomor_urut_tertinggi, no_urut)
            except:
                continue

    nomor_baru = f"{nomor_urut_tertinggi + 1:03}"
    return f"{prefix}{nomor_baru}"

# 🧾 Tambah Tiket Baru
def append_ticket_safely(ticket_data, spreadsheet_id, sheet_name):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    row = [ticket_data[k] for k in [
        "No Ticket", "Tanggal", "Customer", "Lokasi", "Device", "Layanan",
        "Waktu Down Time", "Insiden", "Update Progres", "Perbaikan Gangguan",
        "Up Time", "Status Layanan", "Konfirm PIC", "Status Laporan"
    ]]
    sheet.append_row(row)

# 🔍 Ambil Tiket berdasarkan ID
def get_ticket_by_id(ticket_id, spreadsheet_id, sheet_name):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    records = sheet.get_all_records()

    for i, row in enumerate(records, start=2):
        if row.get("No Ticket", "").strip() == ticket_id.strip():
            return row, i
    return None, None

# ✏️ Update Tiket berdasarkan ID
def update_ticket_by_id(ticket_id, updated_data, spreadsheet_id, sheet_name):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    records = sheet.get_all_records()

    for i, row in enumerate(records, start=2):
        if row.get("No Ticket", "").strip() == ticket_id.strip():
            new_row = [updated_data[k] for k in [
                "No Ticket", "Tanggal", "Customer", "Lokasi", "Device", "Layanan",
                "Waktu Down Time", "Insiden", "Update Progres", "Perbaikan Gangguan",
                "Up Time", "Status Layanan", "Konfirm PIC", "Status Laporan"
            ]]
            sheet.update(f"A{i}:N{i}", [new_row])
            return True
    return False

# 📋 Ambil Data dari Sheet Master
def get_master_data(sheet_name, spreadsheet_id):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    return sheet.get_all_records()

# 🔎 Deteksi Layanan berdasarkan Kode Device dari Master
def detect_layanan_from_device(devices, spreadsheet_id):
    layanan_data = get_master_data("Data Layanan", spreadsheet_id)
    layanan_map = {row["Device"].strip().upper(): row["Layanan"] for row in layanan_data}
    return [layanan_map.get(dev.strip().upper(), "Tidak diketahui") for dev in devices]
