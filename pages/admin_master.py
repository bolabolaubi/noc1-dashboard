import streamlit as st
import pandas as pd
from sheets_connector import connect_sheet, get_master_data

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("⚠️ Anda harus login terlebih dahulu.")
    st.stop()

st.set_page_config(page_title="Admin Master Data", layout="wide")
st.title("⚙️ Admin Master Data")

# ✅ Ambil Spreadsheet ID dari konfigurasi session
spreadsheet_id = st.session_state.get("spreadsheet_id")
if not spreadsheet_id:
    st.warning("⚠️ Spreadsheet belum dipilih. Silakan set di halaman Admin terlebih dahulu.")
    st.stop()

# ============================
# 🔧 Fungsi Tambah Data Unik
# ============================
def tambah_data(sheet_name, data_dict, unique_keys):
    sheet = connect_sheet(spreadsheet_id, sheet_name)
    existing_records = sheet.get_all_records()
    existing_df = pd.DataFrame(existing_records)

    # Cek duplikat berdasarkan kunci unik
    if not existing_df.empty:
        is_duplicate = existing_df[unique_keys].eq(pd.Series(data_dict)[unique_keys]).all(axis=1).any()
        if is_duplicate:
            st.error("❌ Data sudah ada.")
            return

    sheet.append_row(list(data_dict.values()))
    st.success("✅ Data berhasil ditambahkan.")

# ============================
# 📁 Layout Tab
# ============================
tab1, tab2, tab3 = st.tabs(["👥 Data Customer", "🧍 Data PIC", "🧩 Data Layanan"])

# ============================
# 👥 TAB: Customer
# ============================
with tab1:
    st.subheader("➕ Tambah Customer Baru")
    new_customer = st.text_input("Nama Customer")
    if st.button("Tambah Customer", key="add_customer"):
        if new_customer.strip():
            tambah_data("Data Customer", {"Customer": new_customer.strip()}, ["Customer"])

    st.divider()
    st.subheader("📋 Daftar Customer")
    try:
        df_customer = pd.DataFrame(get_master_data("Data Customer", spreadsheet_id))
        st.dataframe(df_customer, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Belum ada data Customer.")
        st.text(str(e))

# ============================
# 🧍 TAB: PIC
# ============================
with tab2:
    st.subheader("➕ Tambah PIC Baru")
    new_pic = st.text_input("Nama PIC")
    if st.button("Tambah PIC", key="add_pic"):
        if new_pic.strip():
            tambah_data("Data PIC", {"PIC": new_pic.strip()}, ["PIC"])

    st.divider()
    st.subheader("📋 Daftar PIC")
    try:
        df_pic = pd.DataFrame(get_master_data("Data PIC", spreadsheet_id))
        st.dataframe(df_pic, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Belum ada data PIC.")
        st.text(str(e))

# ============================
# 🧩 TAB: Layanan
# ============================
with tab3:
    st.subheader("➕ Tambah Relasi Device - Layanan")
    new_device = st.text_input("Kode Device")
    new_layanan = st.text_input("Nama Layanan")
    if st.button("Tambah Layanan", key="add_layanan"):
        if new_device.strip() and new_layanan.strip():
            tambah_data("Data Layanan", {"Device": new_device.strip(), "Layanan": new_layanan.strip()}, ["Device", "Layanan"])

    st.divider()
    st.subheader("📋 Daftar Relasi Device - Layanan")
    try:
        df_layanan = pd.DataFrame(get_master_data("Data Layanan", spreadsheet_id))
        st.dataframe(df_layanan, use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Belum ada data Layanan.")
        st.text(str(e))