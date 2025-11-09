# ---------------- AI Health Tracker (main app) ----------------
from backend.db import init_db
init_db()  # Ensure tables exist before anything else

import streamlit as st
import re
from backend.session_manager import init_session, login_user, logout_user, get_current_user
from backend.auth import create_user, authenticate_user
from backend.password_reset import request_password_reset, reset_password

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="AI Health Tracker", page_icon="🩺", layout="wide")

# Initialize session
init_session()

# Clear transient flags
if "just_logged_in" in st.session_state:
    del st.session_state["just_logged_in"]
if "just_signed_up" in st.session_state:
    del st.session_state["just_signed_up"]

st.title("🩺 AI Health Tracker")
st.markdown("""
Welcome to **AI Lab Report Summarizer**, your personal AI-powered health companion.  
Use the sidebar to navigate between pages like **Upload Reports**, **Dashboard**, **History**, and **Profile**.
""")

# ---------------- Helper: Password Strength Checker ----------------
def check_password_strength(password: str) -> str:
    """Returns Weak / Medium / Strong based on password strength."""
    length = len(password)
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_num = bool(re.search(r"\d", password))
    has_sym = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    score = sum([has_upper, has_lower, has_num, has_sym])

    if length < 6:
        return "Too Short"
    elif score <= 2:
        return "Weak"
    elif score == 3:
        return "Medium"
    else:
        return "Strong"


# ---------------- Login / Signup / Reset ----------------
if not st.session_state.logged_in:
    with st.expander("🔒 Login or Sign Up", expanded=True):
        col1, col2 = st.columns(2)

        # ----------- LOGIN -----------
        with col1:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", use_container_width=True):
                if not email or not password:
                    st.warning("Please enter both email and password.")
                else:
                    try:
                        user = authenticate_user(email.strip(), password.strip())
                        if user:
                            login_user(user.to_dict())
                            st.session_state["just_logged_in"] = True
                            st.success(f"Welcome back, **{user.email}** 🎉")
                            st.experimental_rerun()
                        else:
                            st.error("Invalid email or password.")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # ----------- SIGNUP -----------
        with col2:
            st.subheader("Sign Up")
            su_email = st.text_input("Email", key="signup_email")
            su_name = st.text_input("Full Name (optional)", key="signup_name")
            su_pass = st.text_input("Password", type="password", key="signup_pass")
            su_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")

            # Password strength indicator
            if su_pass:
                strength = check_password_strength(su_pass)
                color = {"Too Short": "red", "Weak": "red", "Medium": "orange", "Strong": "green"}[strength]
                st.markdown(f"**Password Strength:** <span style='color:{color}'>{strength}</span>", unsafe_allow_html=True)

            if st.button("Create Account", use_container_width=True):
                if not su_email or not su_pass:
                    st.warning("Please enter both email and password.")
                elif su_pass != su_pass2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        user = create_user(su_email.strip(), su_pass.strip(), full_name=su_name.strip() or None)
                        login_user(user.to_dict())
                        st.session_state["just_signed_up"] = True
                        st.success("🎉 Account created successfully! You are now logged in.")
                        st.experimental_rerun()
                    except ValueError as e:
                        if "already registered" in str(e).lower():
                            st.error("This email is already registered. Please try logging in instead.")
                        else:
                            st.error(str(e))
                    except Exception as e:
                        st.error(str(e))

    # ----------- PASSWORD RESET SECTION -----------
    with st.expander("🔑 Forgot Password?"):
        reset_email = st.text_input("Enter your registered email:")
        if st.button("Send Reset Link"):
            success, message = request_password_reset(reset_email.strip())
            if success:
                st.success(message)
            else:
                st.error(message)

        reset_code = st.text_input("Enter Reset Code (from email simulation):")
        new_pass = st.text_input("New Password", type="password")
        confirm_new_pass = st.text_input("Confirm New Password", type="password")

        if st.button("Reset Password"):
            if new_pass != confirm_new_pass:
                st.error("Passwords do not match.")
            else:
                success, message = reset_password(reset_code.strip(), new_pass)
                if success:
                    st.success(message)
                else:
                    st.error(message)


# ---------------- Logged-in State ----------------
else:
    current_user = get_current_user()
    st.success(f"✅ Logged in as: **{current_user.get('email')}**")

    st.markdown("---")
    st.subheader("📈 Welcome to Your Health Dashboard")
    st.info("Use the sidebar to upload your lab reports and view AI-generated summaries, graphs, and trends.")

    if st.button("Logout", type="secondary", use_container_width=True):
        logout_user()
        st.info("You have logged out successfully.")
        st.experimental_rerun()
