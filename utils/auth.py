import bcrypt
import streamlit as st

def hash_password(password):
    """Hash a password using bcrypt."""
    # bcrypt.hashpw requires bytes
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def check_password(password, hashed_password):
    """Check a provided password against a hashed password."""
    pwd_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def check_auth():
    """Check if the user is authenticated. If not, redirect to Login page."""
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.switch_page("pages/05_Login.py")

def logout():
    """Clear session state and redirect to login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False
    st.switch_page("pages/05_Login.py")
