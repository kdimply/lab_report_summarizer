import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from backend.session_manager import get_current_user
from backend.database import get_user_history, get_last_two_reports
from backend.visualizer import create_visual_summary

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="History", page_icon="📚", layout="wide")
st.title("📚 Your Report History")

# ---------------- AUTH ----------------
user = get_current_user()
if not user:
    st.warning("⚠️ Please log in to view your history.")
    st.stop()

username = user["email"]

# ---------------- FETCH HISTORY ----------------
history = get_user_history(username)

if not history or len(history) == 0:
    st.info("You haven't uploaded any reports yet.")
    st.stop()

# ---------------- DISPLAY ALL REPORTS ----------------
st.subheader("🗂 All Uploaded Reports")

for report in history:

    upload_time = report["upload_date"].strftime("%Y-%m-%d %H:%M")
    filename = report.get("filename", "Report")

    with st.expander(f"📄 {filename} — {upload_time}"):

        # Summary
        if report.get("summary"):
            st.markdown("### 📝 AI Summary")
            st.write(report["summary"])

        # Diagnosis
        if report.get("diagnosis"):
            st.markdown("### 🩺 Diagnosis / Observation")
            st.info(report["diagnosis"])

        # Tests table
        tests = pd.DataFrame(report["tests"])
        st.markdown("### 🧪 Test Results")
        st.dataframe(tests, use_container_width=True)

        # Chart
        st.markdown("### 📊 Visual Chart")
        fig = create_visual_summary(tests)
        if fig:
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("No chart available for this report.")

st.markdown("---")

# ---------------- COMPARE LAST TWO REPORTS ----------------
st.subheader("📊 Compare Your Last Two Reports")

last_two = get_last_two_reports(username)

if len(last_two) < 2:
    st.info("Upload at least 2 reports to view comparison.")
else:
    latest = last_two[0]
    previous = last_two[1]

    df_latest = pd.DataFrame(latest["tests"])
    df_previous = pd.DataFrame(previous["tests"])

    # Combine based on test name
    comparison = df_latest.merge(
        df_previous,
        on="test_name",
        how="inner",
        suffixes=("_new", "_old")
    )

    st.markdown("### 🧪 Side-by-Side Comparison")
    st.dataframe(comparison, use_container_width=True)

    # Graph for differences
    st.markdown("### 📈 Test Value Changes")

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.scatter(comparison["test_name"], comparison["value_old"], label="Old Value", s=80)
    ax.scatter(comparison["test_name"], comparison["value_new"], label="New Value", s=80)

    for _, row in comparison.iterrows():
        ax.plot(
            [row["test_name"], row["test_name"]],
            [row["value_old"], row["value_new"]],
            color="gray", linestyle="--"
        )

    ax.set_title("Test Value Changes (New vs Previous)")
    ax.set_ylabel("Value")
    ax.set_xticklabels(comparison["test_name"], rotation=45)
    ax.legend()

    st.pyplot(fig)
