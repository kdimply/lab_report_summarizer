# app.py

import streamlit as st
import os
from backend.extractor import process_report
from backend.analyzer import analyze_results
from backend.summarizer import generate_summary
from backend.visualizer import create_visual_summary
from backend.report_generator import generate_pdf_report

st.set_page_config(page_title="Lab Report Summarizer", page_icon="🩺", layout="wide")

st.markdown("<h1 style='text-align: center; color: #4a4a4a;'>AI Lab Report Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #6a6a6a;'>Your Personal Health Report Assistant</h3>", unsafe_allow_html=True)

# Initialize session state variables
if 'processing_done' not in st.session_state:
    st.session_state.processing_done = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

uploaded_file = st.file_uploader("Upload your lab report (PDF or Image) to begin", type=["pdf", "png", "jpg", "jpeg"])

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
            summary = generate_summary(analyzed_df, diagnosis)
            fig = create_visual_summary(analyzed_df)
            
            st.session_state.processed_data = {
                "analyzed_df": analyzed_df,
                "summary": summary,
                "fig": fig,
                "diagnosis": diagnosis,
                "raw_text": raw_text,
            }
    
    os.remove(file_path)
    st.session_state.processing_done = True
    st.rerun()

if st.session_state.processing_done and st.session_state.processed_data:
    data = st.session_state.processed_data
    analyzed_df = data["analyzed_df"]
    summary = data["summary"]
    fig = data["fig"]
    
    st.success("Analysis Complete!")

    # Display the summary and the graph side-by-side
    col1, col2 = st.columns([2, 1.5])
    with col1:
        st.markdown(summary)
    with col2:
        if fig:
            st.pyplot(fig)
        else:
            st.info("A visual graph could not be generated for this report.")

    # --- PDF Download Section ---
    st.markdown("---")
    st.subheader("⬇️ Download Your Simplified Report")
    
    with st.spinner("Generating your PDF report..."):
        chart_path = None
        if fig:
            chart_path = "temp_chart.png"
            fig.savefig(chart_path)

        pdf_path = "Simplified_Lab_Report.pdf"
        generate_pdf_report(analyzed_df, summary, chart_path, pdf_path)
        
        with open(pdf_path, "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(
            label="Download PDF Report",
            data=PDFbyte,
            file_name="Simplified_Lab_Report.pdf",
            mime='application/octet-stream'
        )

        # Clean up temporary files
        if chart_path and os.path.exists(chart_path):
            os.remove(chart_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # --- Detailed Data and Raw Text (in expanders) ---
    with st.expander("Show Detailed Results Table"):
        st.dataframe(analyzed_df)
    
    with st.expander("Show Raw Extracted Text"):
        st.text_area("Raw Text:", data["raw_text"], height=200)

if st.session_state.processing_done:
    if st.button('Analyze Another Report'):
        st.session_state.processing_done = False
        st.session_state.processed_data = None
        st.rerun()