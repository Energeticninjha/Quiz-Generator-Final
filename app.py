import streamlit as st
from utils.database import init_db

st.set_page_config(page_title="Quiz Generator Hub", page_icon="📚", layout="centered")

# Initialize Database
init_db()

# Main routing logic
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("pages/05_Login.py")
else:
    st.switch_page("pages/01_Dashboard.py")
