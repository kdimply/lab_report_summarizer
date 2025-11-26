# Upload_Report.py (FINAL FIXED VERSION)

import streamlit as st
import os
import tempfile
import pandas as pd
from backend.extractor import process_report
from backend.analyzer import analyze_results
from backend.summarizer import generate_summary, find_possible_connections
from backend.report_generator import generate_pdf_report
from backend.ask_ai import get_ai_answer
from backend.session_manager import init_session, get_current_user
from backend.visualizer import create_visual_summary
from backend.database import save_full_report_to_db

# ---------------- INITIAL SETUP ----------------
init_session()
user = get_current_user()

st.set_page_config(page_title="Upload Report", page_icon=" ", layout="wide")
st.title("Upload Your Lab Report")

username = user.get("email") if user else st.text_input("Enter Username (for saving):")

uploaded_file = st.file_uploader(
    "Upload your lab report (PDF or Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

# ---------------- FILE PROCESSING ----------------
if uploaded_file:
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner(" Analyzing your report..."):
        try:
            df, diagnosis, raw_text = process_report(file_path)

            analyzed = analyze_results(df)

            # FIX: Clean numeric values (important for graph + PDF)
            try:
                analyzed["Value Raw"] = analyzed["Value"]
                analyzed["Value"] = (
                    analyzed["Value"]
                    .astype(str)
                    .str.extract(r"([-+]?\d*\.\d+|[-+]?\d+)", expand=False)
                )
                analyzed["Value"] = pd.to_numeric(analyzed["Value"], errors="coerce")
            except Exception:
                pass

            summary = generate_summary(analyzed, diagnosis)
            connections = find_possible_connections(analyzed)

        except Exception as e:
            st.error(f"Error processing report: {e}")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            st.stop()

    st.session_state["last_analysis"] = {
        "df": analyzed,
        "summary": summary,
        "connections": connections,
        "raw_text": raw_text,
        "diagnosis": diagnosis,
        "filename": uploaded_file.name
    }

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

# ---------------- DISPLAY ANALYSIS ----------------
if "last_analysis" in st.session_state:

    data = st.session_state["last_analysis"]
    analyzed = data["df"]
    summary = data["summary"]
    connections = data["connections"]
    raw_text = data["raw_text"]
    diagnosis = data["diagnosis"]
    filename = data["filename"]

    st.success(" Analysis Complete!")

    # --------------------------------------------------------
    # 🟣 FIXED SHORT SUMMARY – SHOW ONLY THE HEADING, NO BULLET
    # --------------------------------------------------------
    short_summary = []
    for line in summary.split("\n"):
        short_summary.append(line)
        if "Here’s what stood out" in line or "Here's what stood out" in line:
            break

    st.markdown("\n".join(short_summary))

    # --------------------------------------------------------
    # FULL SUMMARY IN EXPANDER (no duplication)
    # --------------------------------------------------------
    with st.expander(" View full summary"):
        st.markdown(summary)

    # ---------------- VISUALIZATION ----------------
    fig = None
    try:
        fig = create_visual_summary(analyzed)
    except:
        st.info("Visualization could not be created for this report.")
        fig = None

    chart_path = None
    if fig is not None:
        try:
            fig_obj = getattr(fig, "figure", None)
            if fig_obj is not None:
                fig_to_save = fig_obj
            else:
                fig_to_save = fig

            st.pyplot(fig, use_container_width=True)

            temp_chart = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            chart_path = temp_chart.name
            temp_chart.close()

            fig_to_save.savefig(chart_path, dpi=150, bbox_inches="tight")
        except:
            chart_path = None
            st.info("Visualization save skipped.")
    else:
        st.info("No visual data available for this report.")

    # ---------------- POSSIBLE CONNECTIONS ----------------
    if connections:
        st.markdown("---")
        st.subheader(" Possible Connections")
        for c in connections:
            st.warning(f"• {c}")

    # ---------------- AI QUESTION ANSWER ----------------
    st.markdown("---")
    st.subheader(" Ask AI About Your Report")

    user_question = st.text_input("Ask anything about your results...", key="ai_q")

    if st.button(" Get AI Explanation"):
        if user_question.strip():
            with st.spinner("AI is thinking..."):
                st.session_state["ai_response"] = get_ai_answer(summary, user_question)
        else:
            st.warning("Please enter a question.")

    if "ai_response" in st.session_state:
        st.info(st.session_state["ai_response"])

    # ---------------- SAVE REPORT TO MONGODB ----------------
    if username:
        try:
            safe_df = analyzed.copy().astype(str)
            save_full_report_to_db(
                username=username,
                analyzed_df=safe_df,
                summary=summary,
                diagnosis=diagnosis,
                raw_text=raw_text,
                chart_path=chart_path,
                filename=filename
            )
            st.success(f" Saved to {username}'s history in MongoDB!")
        except Exception as e:
            st.error(f" Save failed: {e}")

    # ---------------- PDF DOWNLOAD ----------------
    st.markdown("---")
    st.subheader("Download PDF Report")

    pdf_path = "Simplified_Lab_Report.pdf"

    try:
        pdf_df = analyzed.copy().astype(str)
        generate_pdf_report(pdf_df, summary, chart_path, pdf_path)

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name="Simplified_Lab_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.error("PDF generation failed.")
    except Exception as e:
        st.error(f"PDF generation failed: {e}")
    finally:
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except:
                pass
        if chart_path and os.path.exists(chart_path):
            try:
                os.remove(chart_path)
            except:
                pass

    # ---------------- DETAILS ----------------
    with st.expander("Detailed Results Table"):
        st.dataframe(analyzed, use_container_width=True)

    with st.expander("Raw Extracted Text"):
        st.text_area("Raw Text:", raw_text, height=200)
