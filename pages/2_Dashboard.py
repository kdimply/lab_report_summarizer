# pages/2_Dashboard.py
import streamlit as st
import pandas as pd
from backend.session_manager import init_session, get_current_user
from backend.database import get_user_history
from backend.comparator import generate_trend_analysis, create_trend_plot

# ---------------- INITIAL SETUP ----------------
init_session()
user = get_current_user()

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.title("📊 Health Dashboard")

# ---------------- AUTH CHECK ----------------
if not user:
    st.warning("🔒 Please log in to view your dashboard.")
    st.stop()

username = user["email"]
st.info(f"Welcome back, **{username}**! Here's your personalized health overview.")

# ---------------- FETCH HISTORY ----------------
history = get_user_history(username)

if not history:
    st.info("You haven't uploaded any lab reports yet. Upload your first report to begin tracking your health!")
    st.stop()

# ---------------- LATEST REPORT ----------------
latest = history[-1]

st.markdown("## 🧪 Latest Report Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**📄 File:** `{latest['filename']}`")
    st.markdown(f"**📅 Uploaded:** {latest['upload_date'].strftime('%Y-%m-%d %H:%M:%S')}")

with col2:
    st.success("This is your most recent health report.")

# Convert tests → DataFrame
latest_df = pd.DataFrame(latest["tests"])

st.markdown("### 📋 Latest Report — Detailed Results")
st.dataframe(latest_df, use_container_width=True)

# ---------------- TREND ANALYSIS ----------------
st.markdown("---")
st.markdown("## 📈 Overall Health Trends")

# Convert full history to DataFrame
trend_rows = []

for report in history:
    for test in report["tests"]:
        trend_rows.append({
            "upload_date": report["upload_date"],
            "test_name": test["test_name"],
            "value": test["value"],
            "status": test["status"]
        })

history_df = pd.DataFrame(trend_rows)

# Generate trend insights
trend_summary, trend_data = generate_trend_analysis(history_df)

st.markdown(f"### 🔍 Trend Summary")
st.info(trend_summary)

# ---------------- TREND VISUALIZATION ----------------
st.markdown("---")
st.subheader("📊 Visualize Test Trends Over Time")

tests_available = sorted(list(trend_data.keys()))

if not tests_available:
    st.info("Not enough trend data yet. Upload more reports to see changes over time.")
else:
    selected_test = st.selectbox("Choose a test to visualize its trend:", tests_available)

    fig = create_trend_plot(trend_data, selected_test)

    if fig:
        st.pyplot(fig)
    else:
        st.warning("Not enough data points to generate a trend chart for this test.")
