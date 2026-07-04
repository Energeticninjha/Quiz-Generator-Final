import streamlit as st
from utils.database import get_user_by_username
from utils.auth import check_password

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

if 'authenticated' in st.session_state and st.session_state.authenticated:
    st.switch_page("pages/01_Dashboard.py")

st.title("🔐 Login to Quiz Generator")
st.markdown("Welcome back! Please login to access your dashboard.")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login", type="primary", use_container_width=True)
    
    if submit:
        user = get_user_by_username(username)
        if user and check_password(password, user['hashed_password']):
            st.session_state.authenticated = True
            st.session_state.user_id = user['id']
            st.session_state.username = user['username']
            st.success("Login successful!")
            st.switch_page("pages/01_Dashboard.py")
        else:
            st.error("Invalid username or password.")

st.markdown("Don't have an account? Navigate to the **Register** page from the sidebar.")
