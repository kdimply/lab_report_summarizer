# 🩺 AI Lab Report Summarizer

This is a mini-project for my AIML course. It's a web application built with Streamlit that uses Optical Character Recognition (OCR) and a custom-trained Named Entity Recognition (NER) model to extract key information from medical lab reports and provide a simple, easy-to-understand summary.

## Features
- **File Upload:** Accepts PDF and image files of lab reports.
- **AI-Powered Extraction:** Uses a custom spaCy NER model to identify test names, values, and diagnoses.
- **Expert System:** Includes a knowledge base to analyze results and provide summaries with food advice.
- **PDF Generation:** Creates and allows downloading a simplified summary report.

## How to Run
1. Clone the repository.
2. Install the required libraries: `pip install -r requirements.txt`
3. Run the Streamlit app: `streamlit run app.py`
