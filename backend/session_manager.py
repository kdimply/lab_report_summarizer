# backend/session_manager.py
import streamlit as st

def init_session():
    """Initialize Streamlit session state for user info."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

def login_user(user_dict):
    """Set user info after successful login."""
    st.session_state.user = user_dict
    st.session_state.username = user_dict.get("email") or user_dict.get("full_name", "")
    st.session_state.logged_in = True

def logout_user():
    """Clear user info and log out."""
    st.session_state.user = None
    st.session_state.username = ""
    st.session_state.logged_in = False

def get_current_user():
    """Return the currently logged-in user's info or None."""
    return st.session_state.user if st.session_state.logged_in else None
