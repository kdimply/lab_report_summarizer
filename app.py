# app.py

import streamlit as st
import os
import pandas as pd

# Import all your backend functions
from backend.extractor import process_report
from backend.analyzer import analyze_results
from backend.summarizer import generate_summary, find_possible_connections
from backend.visualizer import create_visual_summary
from backend.report_generator import generate_pdf_report
from backend.ask_ai import get_ai_answer

st.set_page_config(page_title="Lab Report Summarizer", page_icon="🩺", layout="wide")

# --- UI and Styling ---
st.markdown("<h1 style='text-align: center; color: #4a4a4a;'>AI Lab Report Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #6a6a6a;'>Your Personal Health Report Assistant</h3>", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload your lab report (PDF or Image) to begin", type=["pdf", "png", "jpg", "jpeg"])

# --- Main Processing Logic ---
if uploaded_file is not None and not st.session_state.processing_done:
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner('🔬 Your report is being analyzed by our AI expert system...'):
        extracted_df, diagnosis, raw_text = process_report(file_path)
        
        if extracted_df.empty and not diagnosis:
            st.error("Analysis Failed: Could not extract any valid medical data from the report.")
            st.session_state.processed_data = None
        else:
            analyzed_df = analyze_results(extracted_df)
            
            # Generate all components for the report
            summary = generate_summary(analyzed_df, diagnosis)
            connections = find_possible_connections(analyzed_df)
            fig = create_visual_summary(analyzed_df)
            
            # Store everything in session state
            st.session_state.processed_data = {
                "analyzed_df": analyzed_df, "summary": summary, "fig": fig,
                "diagnosis": diagnosis, "raw_text": raw_text, "connections": connections
            }
    
    os.remove(file_path) # Clean up uploaded file
    st.session_state.processing_done = True
    st.rerun() # Rerun the script to show the results

# --- Display Results ---
if st.session_state.processing_done and st.session_state.processed_data:
    data = st.session_state.processed_data
    
    st.success("Analysis Complete!")

    # Main Display Area
    col1, col2 = st.columns([2, 1.5])
    with col1:
        st.markdown(data["summary"])
        # Feature: Possible Connections
        if data["connections"]:
            st.markdown("---")
            st.subheader("🔗 Possible Connections")
            for insight in data["connections"]:
                st.warning(f"**Insight:** {insight}")
    with col2:
        if data["fig"]:
            st.pyplot(data["fig"])
        else:
            st.info("A visual summary graph could not be generated for this report.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature: Ask AI
    st.markdown("---")
    st.subheader("💬 Ask AI a Question About Your Report")
    user_question = st.text_input("Example: 'What does high LDL mean?' or 'Why is my WBC high?'")
    if st.button("Get AI Explanation"):
        if user_question:
            with st.spinner("AI is thinking..."):
                ai_response = get_ai_answer(data['summary'], user_question)
                st.info(ai_response)
        else:
            st.warning("Please enter a question.")

    # PDF Download and Expanders
    st.markdown("---")
    st.subheader("⬇️ Download Your Simplified Report")
    with st.spinner("Generating your PDF report..."):
        chart_path = "temp_chart.png" if data["fig"] else None
        if chart_path: data["fig"].savefig(chart_path)
        pdf_path = "Simplified_Lab_Report.pdf"
        generate_pdf_report(data["analyzed_df"], data["summary"], chart_path, pdf_path)
        with open(pdf_path, "rb") as pdf_file: PDFbyte = pdf_file.read()
        st.download_button(label="Download PDF Report", data=PDFbyte, file_name="Simplified_Lab_Report.pdf", mime='application/octet-stream')
        if chart_path and os.path.exists(chart_path): os.remove(chart_path)
        if os.path.exists(pdf_path): os.remove(pdf_path)
    
    with st.expander("Show Detailed Results Table"):
        st.dataframe(data["analyzed_df"])
    with st.expander("Show Raw Extracted Text"):
        st.text_area("Raw Text:", data["raw_text"], height=200)

if st.session_state.processing_done:
    if st.button('Analyze Another Report'):
        st.session_state.processing_done = False
        st.session_state.processed_data = None
        st.rerun()