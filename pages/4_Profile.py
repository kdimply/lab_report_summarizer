# pages/4_Profile.py
import streamlit as st
import pandas as pd
from backend.session_manager import init_session, get_current_user
from backend.database import get_user_history

# ---- Initialize Session ----
init_session()
user = get_current_user()

st.title("👤 Profile & Account Overview")

# ---- Authentication Check ----
if not user:
    st.warning("Please log in to view your profile.")
    st.stop()

# ---- User Info ----
email = user.get("email", "Not Provided")
full_name = user.get("full_name", "Not Provided")
dob = user.get("dob", "Not Provided")
age = user.get("age", "Not Provided")

# ---- Profile Header ----
st.subheader("Your Profile Details")

col1, col2 = st.columns(2)

with col1:
    st.write(f"**Full Name:** {full_name}")
    st.write(f"**Email:** {email}")

with col2:
    st.write(f"**Date of Birth:** {dob}")
    st.write(f"**Age:** {age}")

st.markdown("---")

# ---- Fetch Report History ----
history = get_user_history(email)

if not history:
    st.info("No reports uploaded yet.")
    st.stop()

# ---- Convert History into a DataFrame ----
history_df_rows = []
for report in history:
    for test in report["tests"]:
        history_df_rows.append({
            "upload_date": report["upload_date"],
            "filename": report["filename"],
            "test_name": test["test_name"],
            "value": test["value"],
            "status": test["status"],
        })

history_df = pd.DataFrame(history_df_rows)

# ---- Account Summary ----
st.subheader("Account Summary")

st.write(f"**Total Reports:** {len(history)}")
st.write(f"**Unique Tests Tracked:** {history_df['test_name'].nunique()}")
st.write(f"**Most Recent File:** {history[-1]['filename']}")

st.markdown("---")

# ---- Frequently Abnormal Tests ----
st.subheader("Frequently Abnormal Tests")

abnormal_df = history_df[history_df["status"] != "Normal"]

if abnormal_df.empty:
    st.success("All your results have been normal recently 🎉")
else:
    abnormal_count = (
        abnormal_df.groupby("test_name")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="abnormal_count")
    )
    st.dataframe(abnormal_count, use_container_width=True)

st.markdown("---")

# ---- Full Test History ----
st.subheader("Full Test History")
st.dataframe(history_df.sort_values("upload_date"), use_container_width=True)
