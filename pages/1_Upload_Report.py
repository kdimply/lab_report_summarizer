import streamlit as st
import os
from backend.extractor import process_report
from backend.analyzer import analyze_results
from backend.summarizer import generate_summary, find_possible_connections
from backend.report_generator import generate_pdf_report
from backend.ask_ai import get_ai_answer
from backend.database import save_report_to_db
from backend.session_manager import init_session, get_current_user
from backend.visualizer import create_visual_summary  # ✅ For bar chart visualization

# ---------------- INITIAL SETUP ----------------
init_session()
user = get_current_user()

st.set_page_config(page_title="Upload Report", page_icon="📤", layout="wide")
st.title("📤 Upload Your Lab Report")

# Determine username
username = user.get("email") if user else st.text_input("Enter Username (for saving):")

uploaded_file = st.file_uploader("Upload your lab report (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

# ---------------- FILE PROCESSING ----------------
if uploaded_file:
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("🔬 Analyzing your report... Please wait..."):
        try:
            df, diagnosis, raw_text = process_report(file_path)
            analyzed = analyze_results(df)
            summary = generate_summary(analyzed, diagnosis)
            connections = find_possible_connections(analyzed)
        except Exception as e:
            st.error(f"Error processing the report: {e}")
            st.stop()

    # ✅ store in session so reruns (AI clicks) don’t reset analysis
    st.session_state["last_analysis"] = {
        "df": analyzed,
        "summary": summary,
        "connections": connections,
        "raw_text": raw_text,
        "diagnosis": diagnosis,
        "filename": uploaded_file.name
    }

    # Clean up uploaded file
    if os.path.exists(file_path):
        os.remove(file_path)

# ---------------- DISPLAY ANALYSIS IF AVAILABLE ----------------
if "last_analysis" in st.session_state:
    data = st.session_state["last_analysis"]
    analyzed = data["df"]
    summary = data["summary"]
    connections = data["connections"]
    raw_text = data["raw_text"]
    diagnosis = data["diagnosis"]
    filename = data["filename"]

    st.success("✅ Analysis Complete!")

    # ---------------- SUMMARY ----------------

    st.markdown(summary)

    # ---------------- VISUALIZATION ----------------
    st.markdown("---")
    st.subheader("📊 Visual Summary of Test Results")

    fig = create_visual_summary(analyzed)
    if fig:
        st.pyplot(fig, use_container_width=True)
    else:
        st.info("No visual data available for this report.")

    # ---------------- POSSIBLE CONNECTIONS ----------------
    if connections:
        st.markdown("---")
        st.subheader("🔗 Possible Connections")
        for c in connections:
            st.warning(f"**Insight:** {c}")

    # ---------------- AI EXPLAINER SECTION ----------------
    st.markdown("---")
    st.subheader("💬 Ask AI About Your Report")

    user_question = st.text_input(
        "Type your question (e.g., 'What does high LDL mean?' or 'Why is my WBC slightly low?')",
        placeholder="Ask me about any test result from your report...",
        key="ai_question"
    )

    if st.button("🤖 Get AI Explanation", use_container_width=True):
        if user_question.strip():
            with st.spinner("AI is analyzing your question..."):
                ai_response = get_ai_answer(summary, user_question)
                st.session_state["ai_response"] = ai_response
        else:
            st.warning("Please enter a question before asking.")

    if "ai_response" in st.session_state:
        st.info(st.session_state["ai_response"])

    # ---------------- SAVE REPORT ----------------
    if username:
        try:
            save_report_to_db(username, analyzed, diagnosis, filename=filename)
            st.success(f"💾 Report saved to {username}'s account.")
        except Exception as e:
            st.error(f"Error saving report: {e}")

    # ---------------- PDF DOWNLOAD ----------------
    st.markdown("---")
    st.subheader("⬇️ Download Your Simplified Report")

    pdf_path = "Simplified_Lab_Report.pdf"
    try:
        generate_pdf_report(analyzed, summary, None, pdf_path)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_file,
                file_name="Simplified_Lab_Report.pdf",
                mime="application/octet-stream",
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Could not generate PDF: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # ---------------- EXTRA DETAILS ----------------
    with st.expander("📋 Show Detailed Results Table"):
        st.dataframe(analyzed, use_container_width=True)

    with st.expander("🧾 Show Raw Extracted Text"):
        st.text_area("Raw Text:", raw_text, height=200)
