# backend/extractor.py

import pytesseract
from PIL import Image
import pdfplumber
import pandas as pd
import os
import spacy
from thefuzz import process # Import the fuzzy matching library

# Your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ --- NEW: OUR DICTIONARY OF "REAL" TEST NAMES ---
# This is the 'master list' we will match against. It's our 'expert knowledge'.
VALID_TEST_NAMES = [
    'HEMOGLOBIN', 'RBC COUNT', 'WBC COUNT', 'PLATELET COUNT', 'HEMATOCRIT', 
    'MCV', 'MCH', 'MCHC', 'RDW', 'TOTAL CHOLESTEROL', 'LDL CHOLESTEROL', 
    'HDL CHOLESTEROL', 'TRIGLYCERIDES', 'GLUCOSE', 'CREATININE', 'UREA', 
    'SODIUM', 'POTASSIUM', 'ALT', 'AST', 'BILIRUBIN', 'TSH', 'T3', 'T4', 
    'VITAMIN B12', 'VITAMIN D', 'SERUM IRON'
]
# ----------------------------------------------------

# Load the model safely
try:
    nlp_ner = spacy.load("./ner_model")
except OSError:
    nlp_ner = None 

def extract_text_from_image(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        return f"Error processing image: {e}"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error processing PDF: {e}"

def correct_test_name(messy_name):
    """
    Uses fuzzy string matching to find the best match for a messy test name
    from our list of valid names.
    """
    # process.extractOne returns a tuple: (best_match, score)
    best_match, score = process.extractOne(messy_name.upper(), VALID_TEST_NAMES)
    
    # We set a threshold of 75. If the match is not at least 75% similar, 
    # we discard it as it's likely just junk.
    if score > 75:
        return best_match
    return None

def parse_lab_report(text):
    if nlp_ner is None:
        return pd.DataFrame(), None, "NER model not loaded. Please train the model first."

    doc = nlp_ner(text)
    results = []
    diagnoses = []
    
    for ent in doc.ents:
        if ent.label_ == 'DIAGNOSIS':
            diagnoses.append(ent.text)
        elif ent.label_ == 'TEST_NAME':
            # ✅ --- THE SELF-CORRECTION STEP ---
            corrected_name = correct_test_name(ent.text)
            
            # We only proceed if the name was corrected to a valid one
            if corrected_name:
                value_text = text[ent.end_char:].split('\n')[0].strip()
                if value_text:
                    value_match = pd.to_numeric(value_text.split()[0], errors='coerce')
                    if not pd.isna(value_match):
                        results.append({"Test Name": corrected_name, "Value": value_match})

    final_diagnosis = ". ".join(diagnoses) if diagnoses else None
    
    return pd.DataFrame(results), final_diagnosis, None

def process_report(file_path):
    _, file_extension = os.path.splitext(file_path)
    text = ""
    if file_extension.lower() == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension.lower() in ['.png', 'jpg', 'jpeg']:
        text = extract_text_from_image(file_path)
    else:
        return pd.DataFrame(), None, "Unsupported file type."

    if "Error" in text:
        return pd.DataFrame(), None, text
        
    df, diagnosis, error = parse_lab_report(text) 
    
    if error:
        return pd.DataFrame(), None, error
        
    return df, diagnosis, text