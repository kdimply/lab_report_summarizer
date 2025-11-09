# pages/3_History.py
import streamlit as st
from backend.session_manager import init_session, get_current_user
from backend.database import get_user_history
import pandas as pd

# --- Initialize session and get user ---
init_session()
user = get_current_user()

st.title("🕒 Report History")

# --- Authentication check ---
if not user:
    st.warning("🔒 Please log in to view your report history.")
    st.stop()

username = user.get("email")
st.info(f"Showing report history for **{username}**")

# --- Get user history ---
history_df = get_user_history(username)

if history_df.empty:
    st.info("No reports uploaded yet. Go to the **Upload Report** page to add your first one.")
else:
    # Sort newest first
    history_df = history_df.sort_values(by="upload_date", ascending=False)

    st.markdown("## 📄 Past Reports")
    st.dataframe(
        history_df,
        column_config={
            "test_name": "Test Name",
            "value": "Value",
            "status": "Status",
            "upload_date": "Upload Date"
        },
        use_container_width=True
    )

    # Summary stats
    st.markdown("---")
    st.subheader("📊 Summary Statistics")
    test_count = len(history_df["test_name"].unique())
    total_reports = len(history_df["upload_date"].unique())
    abnormal = history_df[history_df["status"] != "Normal"]

    st.metric("Total Unique Tests", test_count)
    st.metric("Total Reports Uploaded", total_reports)
    st.metric("Abnormal Results", len(abnormal))

    if not abnormal.empty:
        st.markdown("### ⚠️ Recent Abnormal Results")
        st.dataframe(abnormal[["test_name", "value", "status", "upload_date"]])
