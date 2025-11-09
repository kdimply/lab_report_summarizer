# pages/2_Dashboard.py
import streamlit as st
from backend.session_manager import init_session, get_current_user
from backend.database import get_user_history
from backend.comparator import generate_trend_analysis, create_trend_plot

# --- Initialize session and get user ---
init_session()
user = get_current_user()

st.title("📊 Health Dashboard")

# --- Authentication check ---
if not user:
    st.warning("🔒 Please log in to view your personalized dashboard.")
    st.stop()

username = user.get("email")

st.info(f"Welcome back, **{username}**! Here’s your health overview.")

# --- Fetch user data ---
history_df = get_user_history(username)

if history_df.empty:
    st.info("No reports found yet. Upload a report on the **Upload** page to get started.")
else:
    # --- Generate trend summary ---
    st.markdown("## 📈 Health Trends")
    trend_summary, trend_data = generate_trend_analysis(history_df)
    st.markdown(trend_summary)

    # --- Trend chart selection ---
    st.markdown("---")
    st.subheader("📊 Visualize Your Test Trends")
    tests = sorted(list(trend_data.keys()))

    if tests:
        test_to_plot = st.selectbox("Select a test to visualize:", tests)
        if test_to_plot:
            fig = create_trend_plot(trend_data, test_to_plot)
            st.pyplot(fig)
    else:
        st.info("No test data available for plotting yet.")
