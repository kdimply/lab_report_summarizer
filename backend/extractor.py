# extractor.py (updated)
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import pdfplumber
import pandas as pd
import os
import re
from thefuzz import process

# Set OCR path (keep your configuration)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

VALID_TEST_NAMES = [
    "HEMOGLOBIN", "HEMATOCRIT", "RBC", "RBC COUNT", "WBC", "WBC COUNT",
    "NEUTROPHILS", "LYMPHOCYTES", "MONOCYTES", "MCV", "MCH", "MCHC", "RDW",
    "PLATELET", "PLATELET COUNT",
    "TOTAL CHOLESTEROL", "LDL CHOLESTEROL", "HDL CHOLESTEROL", "TRIGLYCERIDES",
    "GLUCOSE", "HBA1C", "UREA", "CREATININE",
    "SODIUM", "POTASSIUM",
    "ALT", "AST", "BILIRUBIN",
    "TSH", "T3", "T4",
    "VITAMIN D", "VITAMIN B12", "SERUM IRON"
]

# ----------- IMAGE PREPROCESSING -----------
def preprocess_image(img):
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2)
    img = ImageEnhance.Brightness(img).enhance(1.2)
    return img

# ----------- TEXT EXTRACTION -----------
def extract_text_from_pdf(path):
    try:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += "\n" + t
        return text if text.strip() else "Error: No text"
    except Exception as e:
        return f"Error: PDF failed ({e})"

def extract_text_from_image(path):
    try:
        img = Image.open(path)
        img = preprocess_image(img)
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"Error: Image failed ({e})"

# ----------- TEST NAME CORRECTION -----------
def correct_test_name(name):
    if not isinstance(name, str):
        return None
    name = re.sub(r'[^A-Za-z0-9 ]', ' ', name).upper().strip()
    best, score = process.extractOne(name, VALID_TEST_NAMES)
    return best if score and score > 65 else None

# ----------- REFERENCE RANGE PARSING -----------
def parse_reference_range(raw_range):
    if not raw_range or str(raw_range).strip().upper() in ("NONE", "N/A", "NAN"):
        return None
    s = str(raw_range).strip()
    s_clean = s.replace("(", "").replace(")", "").replace("NORMAL RANGE", "").replace("REFERENCE", "").strip()

    # comparator formats < or >
    m = re.search(r'([<>])\s*([0-9]+(?:\.[0-9]+)?)', s_clean)
    if m:
        op, num = m.group(1), float(m.group(2))
        return (None, float(num), op)

    # inclusive ranges like 13 - 17 or 13.0-17.0 or en-dash
    m2 = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*[-–—]\s*([0-9]+(?:\.[0-9]+)?)', s_clean)
    if m2:
        low, high = float(m2.group(1)), float(m2.group(2))
        return (low, high, None)

    # single number fallback
    m3 = re.search(r'([0-9]+(?:\.[0-9]+)?)', s_clean)
    if m3:
        num = float(m3.group(1))
        if '<' in s or 'LESS' in s.upper():
            return (None, num, '<')
        if '>' in s or 'GREATER' in s.upper():
            return (num, None, '>')
        return (num, None, None)
    return None

# ----------- VALUE & UNIT PARSING -----------
def parse_value_and_unit(raw_value):
    if raw_value is None:
        return None, ""
    s = str(raw_value).strip()
    # numeric with possible scientific notation and percentage
    m = re.search(r'([-+]?\d*\.\d+|\d+e[+-]?\d+|\d+)', s, flags=re.I)
    if not m:
        return None, ""
    num = m.group(0)
    try:
        val = float(num)
    except:
        try:
            val = float(num.replace(',', ''))
        except:
            return None, ""
    unit = s[m.end():].strip()
    if unit == "%" or unit.startswith("%"):
        unit = "%"
    return val, unit

# ----------- MAIN PARSER -----------
def parse_report_text(text):
    text = text.replace("—", "-").replace("–", "-").replace("|", " ").replace("•", " ")
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    records = []
    # stricter regex: name followed by number (with optional unit) and optional parenthesized range
    for line in lines:
        # try to capture: NAME <space> VALUE[unit] (RANGE)
        m = re.search(
            r'([A-Za-z][A-Za-z \(\)\-]{1,60}?)\s+([-+]?\d*\.\d+|\d+e[+-]?\d+|\d+)\s*([A-Za-z%/µg\.\d]*)\s*(\([^\)]*\))?',
            line
        )
        if not m:
            # fallback looser but still anchored
            m = re.search(
                r'([A-Za-z][A-Za-z \(\)\-]{1,60}?)[:\-\s]\s*([-+]?\d*\.\d+|\d+e[+-]?\d+|\d+)\s*([A-Za-z%/µg\.\d]*)',
                line
            )
        if not m:
            continue

        raw_name = m.group(1).strip()
        raw_value = m.group(2).strip()
        raw_unit = m.group(3).strip() if m.lastindex and m.lastindex >= 3 else ""
        raw_range = m.group(4).strip() if m.lastindex and m.lastindex >= 4 and m.group(4) else None

        fixed_name = correct_test_name(raw_name)
        if not fixed_name:
            continue

        # parse numeric value + unit
        val, unit = parse_value_and_unit(raw_value + (" " + raw_unit if raw_unit else ""))
        if val is None:
            continue

        parsed_range = parse_reference_range(raw_range) if raw_range else None

        records.append({
            "Test Name": fixed_name,
            "Value": val,
            "Unit": unit,
            "Reference Range Raw": raw_range if raw_range else "",
            "Reference Range Parsed": parsed_range
        })

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["Test Name"] = df["Test Name"].astype(str)
    df["Reference Range Raw"] = df["Reference Range Raw"].astype(str)
    return df

# ----------- MAIN ENTRY POINT -----------
def process_report(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        text = extract_text_from_image(file_path)

    if not text or "Error" in text:
        return pd.DataFrame(), None, text

    df = parse_report_text(text)

    if df.empty:
        return pd.DataFrame(), None, "Could not detect test values from the report."

    return df, None, text
