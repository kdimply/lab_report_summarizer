# ---------------- AI Health Tracker (main app) ----------------

import streamlit as st
import re
from datetime import datetime

from backend.session_manager import init_session, login_user, logout_user, get_current_user
from backend.auth import create_user, authenticate_user
from backend.password_reset import request_password_reset, reset_password

# ---------------- Streamlit Setup ----------------
st.set_page_config(page_title="AI Health Tracker", page_icon="🩺", layout="wide")

# Initialize session
init_session()

# Clear temporary flags
st.session_state.pop("just_logged_in", None)
st.session_state.pop("just_signed_up", None)

# ---------------- App Header ----------------
st.title("🩺 AI Health Tracker")
st.markdown("""
Welcome to **AI Lab Report Summarizer**, your AI-powered health assistant.  
Navigate using the sidebar:  
👉 **Upload Reports**, **Dashboard**, **History**, **Profile**.
""")

# ---------------- Password Strength Checker ----------------
def check_password_strength(password: str) -> str:
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

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:

    with st.expander("🔒 Login or Sign Up", expanded=True):

        col1, col2 = st.columns(2)

        # ----------- LOGIN ----------- #
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

                            # Save full details in session
                            login_user({
                                "email": user["email"],
                                "full_name": user.get("full_name", "Not Provided"),
                                "dob": user.get("dob", "Not Provided"),
                                "age": user.get("age", "Not Provided")
                            })

                            st.session_state["just_logged_in"] = True
                            st.success(f"Welcome back, **{user['email']}** 🎉")
                            st.rerun()

                        else:
                            st.error("Invalid email or password.")

                    except Exception as e:
                        st.error(f"Error: {e}")

        # ----------- SIGNUP ----------- #
        with col2:
            st.subheader("Sign Up")

            su_email = st.text_input("Email", key="signup_email")
            su_name = st.text_input("Full Name", key="signup_name")

            su_dob = st.date_input(
                "Date of Birth",
                min_value=datetime(1900, 1, 1),
                max_value=datetime.today(),
                key="signup_dob"
            )

            su_pass = st.text_input("Password", type="password", key="signup_pass")
            su_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")

            # Password strength meter
            if su_pass:
                strength = check_password_strength(su_pass)
                colors = {"Too Short": "red", "Weak": "red", "Medium": "orange", "Strong": "green"}
                st.markdown(
                    f"**Password Strength:** <span style='color:{colors[strength]}'>{strength}</span>",
                    unsafe_allow_html=True
                )

            if st.button("Create Account", use_container_width=True):
                if not su_email or not su_pass:
                    st.warning("Please enter both email and password.")

                elif su_pass != su_pass2:
                    st.error("Passwords do not match.")

                else:
                    try:
                        dob_str = su_dob.strftime("%Y-%m-%d")

                        user = create_user(
                            su_email.strip(),
                            su_pass.strip(),
                            full_name=su_name.strip() if su_name else None,
                            dob=dob_str
                        )

                        # Save into session for immediate login
                        login_user({
                            "email": user["email"],
                            "full_name": user.get("full_name", "Not Provided"),
                            "dob": user.get("dob", "Not Provided"),
                            "age": user.get("age", "Not Provided")
                        })

                        st.session_state["just_signed_up"] = True
                        st.success("🎉 Account created successfully! You are now logged in.")
                        st.rerun()

                    except ValueError as e:
                        if "already registered" in str(e).lower():
                            st.error("This email is already registered.")
                        else:
                            st.error(str(e))

                    except Exception as e:
                        st.error(str(e))

    # ----------- PASSWORD RESET SECTION ----------- #
    with st.expander("🔑 Forgot Password?"):
        reset_email = st.text_input("Enter your registered email:")
        if st.button("Send Reset Link"):
            success, msg = request_password_reset(reset_email.strip())
            st.success(msg) if success else st.error(msg)

        reset_code = st.text_input("Enter Reset Code:")
        new_pass = st.text_input("New Password", type="password")
        confirm_new_pass = st.text_input("Confirm New Password", type="password")

        if st.button("Reset Password"):
            if new_pass != confirm_new_pass:
                st.error("Passwords do not match.")
            else:
                success, msg = reset_password(reset_code.strip(), new_pass)
                st.success(msg) if success else st.error(msg)

# ---------------- LOGGED-IN STATE ----------------
else:
    current_user = get_current_user()

    st.success(f"✅ Logged in as: **{current_user.get('email')}**")

    st.markdown("---")
    st.subheader("📈 Welcome to Your Health Dashboard")
    st.info("Use the sidebar to upload your lab reports, view summaries, graphs, and trends.")

    if st.button("Logout", type="secondary", use_container_width=True):
        logout_user()
        st.info("You have logged out successfully.")
        st.rerun()
