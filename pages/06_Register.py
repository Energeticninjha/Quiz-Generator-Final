import streamlit as st
from utils.database import create_user
from utils.auth import hash_password

st.set_page_config(page_title="Register", page_icon="📝", layout="centered")

if 'authenticated' in st.session_state and st.session_state.authenticated:
    st.switch_page("pages/01_Dashboard.py")

st.title("📝 Create an Account")
st.markdown("Join us to start generating intelligent quizzes!")

with st.form("register_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    submit = st.form_submit_button("Register", type="primary", use_container_width=True)
    
    if submit:
        if not username or not email or not password:
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            hashed = hash_password(password)
            user_id = create_user(username, email, hashed)
            if user_id:
                st.success("Registration successful! Logging you in...")
                st.session_state.authenticated = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.switch_page("pages/01_Dashboard.py")
            else:
                st.error("Username or email already exists. Please choose a different one.")
