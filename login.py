# login.py

import streamlit as st

# Konfigurasi halaman
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login ke Aplikasi NOC")

# Form login
username = st.text_input("Username")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

# Proses login sederhana (hardcoded)
if login_button:
    if username == "admin" and password == "admin123":
        st.session_state["authenticated"] = True
        st.success("✅ Login berhasil!")
        st.switch_page("pages/dashboard.py")  # Ganti sesuai nama file dashboard kamu
    else:
        st.error("❌ Username atau password salah")
