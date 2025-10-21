# backend/extractor.py

import pytesseract
from PIL import Image
import pdfplumber
import pandas as pd
import os
import spacy
import re
from thefuzz import process

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Our 'master list' of valid test names for self-correction
VALID_TEST_NAMES = [
    'HEMOGLOBIN', 'RBC COUNT', 'WBC COUNT', 'PLATELET COUNT', 'HEMATOCRIT', 
    'MCV', 'MCH', 'MCHC', 'RDW', 'TOTAL CHOLESTEROL', 'LDL CHOLESTEROL', 
    'HDL CHOLESTEROL', 'TRIGLYCERIDES', 'GLUCOSE', 'HBA1C', 'CREATININE', 'UREA', 
    'SODIUM', 'POTASSIUM', 'ALT', 'AST', 'BILIRUBIN', 'TSH', 'T3', 'T4', 
    'VITAMIN B12', 'VITAMIN D', 'SERUM IRON', 'LYMPHOCYTES', 'NEUTROPHILS', 'MONOCYTES'
]

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
    """Uses fuzzy string matching to find the best match for a messy test name."""
    best_match, score = process.extractOne(messy_name.upper(), VALID_TEST_NAMES)
    if score > 70: # Lowered threshold slightly for more flexibility
        return best_match
    return None

def parse_lab_report(text):
    """
    A more advanced parser that can handle multi-line entities and self-corrects test names.
    """
    if nlp_ner is None:
        return pd.DataFrame(), None, "NER model not loaded. Please train the model first."

    doc = nlp_ner(text)
    results = []
    diagnoses = []
    
    # First, extract all entities and their positions
    entities = [{'text': ent.text, 'label': ent.label_, 'start': ent.start_char, 'end': ent.end_char} for ent in doc.ents]
    
    # Process diagnoses separately
    for ent in entities:
        if ent['label'] == 'DIAGNOSIS':
            diagnoses.append(ent['text'])
    
    # Group Test Names with their nearby Values and Ranges
    test_entities = [ent for ent in entities if ent['label'] == 'TEST_NAME']
    value_entities = [ent for ent in entities if ent['label'] == 'VALUE']
    range_entities = [ent for ent in entities if ent['label'] == 'REFERENCE_RANGE']

    for test_ent in test_entities:
        corrected_name = correct_test_name(test_ent['text'])
        if not corrected_name:
            continue # Skip if the test name is not valid

        current_result = {"Test Name": corrected_name}
        
        # Define a search window to find associated values/ranges (e.g., within the next 50 characters)
        search_window = 50 
        
        # Find the closest VALUE entity within the window
        closest_value = None
        min_dist_val = float('inf')
        for val_ent in value_entities:
            dist = val_ent['start'] - test_ent['end']
            if 0 <= dist < min_dist_val and dist < search_window:
                min_dist_val = dist
                closest_value = val_ent
        
        if closest_value:
            try:
                current_result["Value"] = float(closest_value['text'])
            except ValueError:
                continue # Skip if value is not a number

        # Find the closest REFERENCE_RANGE entity within the window
        closest_range = None
        min_dist_range = float('inf')
        for range_ent in range_entities:
            dist = range_ent['start'] - test_ent['end']
            if 0 <= dist < min_dist_range and dist < search_window:
                min_dist_range = dist
                closest_range = range_ent
        
        if closest_range:
            current_result["Reference Range"] = closest_range['text']

        if "Value" in current_result:
             results.append(current_result)

    final_diagnosis = ". ".join(diagnoses) if diagnoses else None
    
    # Remove duplicate results if any, keeping the first one
    df = pd.DataFrame(results)
    df = df.drop_duplicates(subset=['Test Name'], keep='first')
    
    return df, final_diagnosis, None

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