import streamlit as st

st.set_page_config(page_title="🔧 Admin - Konfigurasi Spreadsheet")

st.title("⚙️ Menu Admin - Konfigurasi Spreadsheet")

# 🔧 Form konfigurasi Spreadsheet
with st.form("config_form"):
    spreadsheet_id = st.text_input("🆔 Spreadsheet ID", value=st.session_state.get("spreadsheet_id", ""))
    sheet_name = st.text_input("📄 Sheet Name", value=st.session_state.get("sheet_name", ""))
    simpan = st.form_submit_button("💾 Simpan Konfigurasi")

    if simpan:
        st.session_state["spreadsheet_id"] = spreadsheet_id
        st.session_state["sheet_name"] = sheet_name
        st.success("✅ Konfigurasi berhasil disimpan!")

# ℹ️ Tampilkan konfigurasi aktif
if "spreadsheet_id" in st.session_state and "sheet_name" in st.session_state:
    st.info(f"""
    🔍 Konfigurasi Aktif:
    - **Spreadsheet ID:** `{st.session_state["spreadsheet_id"]}`
    - **Sheet Name:** `{st.session_state["sheet_name"]}`
    """)
else:
    st.warning("⚠️ Belum ada konfigurasi yang disimpan.")
