# login.py

import streamlit as st
import hashlib
from sheets_connector import connect_sheet

# Konfigurasi halaman
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login ke Aplikasi NOC")

# Ambil spreadsheet ID
spreadsheet_id = st.secrets.get("config", {}).get("spreadsheet_id")
if not spreadsheet_id:
    st.error("❌ Konfigurasi spreadsheet_id tidak ditemukan di secrets.")
    st.stop()

# Fungsi hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Ambil data admin dari sheet
@st.cache_data(ttl=300)
def load_admin_data():
    sheet = connect_sheet(spreadsheet_id, "Admin Data")
    return sheet.get_all_records()

# Form login
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

# Proses login
if login_button:
    admin_data = load_admin_data()
    user_found = next((row for row in admin_data if row["Username"].strip() == username.strip()), None)

    if user_found and user_found["Password"] == hash_password(password):
        st.session_state["authenticated"] = True
        st.success("✅ Login berhasil!")
        st.switch_page("pages/dashboard.py")  # Sesuaikan dengan nama halaman utama kamu
    else:
        st.error("❌ Username atau password salah")
