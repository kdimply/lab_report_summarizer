# pages/4_Profile.py
import streamlit as st
import pandas as pd
from backend.session_manager import init_session, get_current_user
from backend.database import get_user_history

# Initialize user session
init_session()
user = get_current_user()

st.title("👤 Profile & Account Overview")

# --- Authentication Check ---
if not user:
    st.warning("🔒 Please log in to view your profile.")
    st.stop()

username = user.get("email")
st.success(f"Welcome, **{username}**!")

# --- Fetch user history ---
history_df = get_user_history(username)

# --- Profile Summary Section ---
st.markdown("## 🩺 Account Summary")

if history_df.empty:
    st.info("You haven't uploaded any reports yet. Go to the **Upload Report** page to get started.")
else:
    total_reports = len(history_df["upload_date"].unique())
    total_tests = len(history_df)
    unique_tests = len(history_df["test_name"].unique())
    abnormal = len(history_df[history_df["status"] != "Normal"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Total Reports", total_reports)
    col2.metric("🧪 Total Tests", total_tests)
    col3.metric("🔁 Unique Tests", unique_tests)
    col4.metric("⚠️ Abnormal Results", abnormal)

# --- Download Section ---
st.markdown("---")
st.subheader("📦 Export Your Health Data")

if not history_df.empty:
    # Convert to Excel and CSV
    csv_data = history_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"{username}_health_data.csv",
        mime="text/csv",
        help="Download all your report data as a CSV file"
    )

    excel_buffer = pd.ExcelWriter(f"{username}_health_data.xlsx", engine="xlsxwriter")
    history_df.to_excel(excel_buffer, index=False, sheet_name="Reports")
    excel_buffer.close()
    with open(f"{username}_health_data.xlsx", "rb") as file:
        st.download_button(
            label="📘 Download Excel",
            data=file.read(),
            file_name=f"{username}_health_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("No data to export yet.")

# --- Optional: Account Info Section ---
st.markdown("---")
st.subheader("🧍 Account Details")

st.write(f"**Email:** {username}")
if "full_name" in user and user["full_name"]:
    st.write(f"**Full Name:** {user['full_name']}")
else:
    st.write("**Full Name:** Not provided")

st.write("**Account Created:** (coming soon)")
st.caption("All your data is securely stored and only visible to you.")
