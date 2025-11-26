# test_data.py
import re

def normalize_spaces(text):
    return re.sub(r"\s+", " ", text).strip()

def make(text, labels):
    clean_text = normalize_spaces(text)
    entities = []
    for label, substring in labels.items():
        clean_sub = normalize_spaces(substring)
        start = clean_text.find(clean_sub)
        if start == -1:
            raise ValueError(f"Could not align: {clean_sub} in {clean_text}")
        end = start + len(clean_sub)
        entities.append((start, end, label))
    return (clean_text, {"entities": entities})


# 20 clean samples for testing
TEST_DATA = [
    make("Hemoglobin 10.4 g/dL (11.0-14.5)",
         {"TEST_NAME": "Hemoglobin", "VALUE": "10.4 g/dL", "REFERENCE_RANGE": "(11.0-14.5)"}),

    make("Hemoglobin 13.8 g/dL (13.0-17.0)",
         {"TEST_NAME": "Hemoglobin", "VALUE": "13.8 g/dL", "REFERENCE_RANGE": "(13.0-17.0)"}),

    make("WBC Count 15000 /µL (4500-11000)",
         {"TEST_NAME": "WBC Count", "VALUE": "15000 /µL", "REFERENCE_RANGE": "(4500-11000)"}),

    make("WBC Count 7800 /µL (4500-11000)",
         {"TEST_NAME": "WBC Count", "VALUE": "7800 /µL", "REFERENCE_RANGE": "(4500-11000)"}),

    make("Platelet Count 200000 /µL (150000-450000)",
         {"TEST_NAME": "Platelet Count", "VALUE": "200000 /µL", "REFERENCE_RANGE": "(150000-450000)"}),

    make("Triglycerides 180 mg/dL (<150)",
         {"TEST_NAME": "Triglycerides", "VALUE": "180 mg/dL", "REFERENCE_RANGE": "(<150)"}),

    make("HDL Cholesterol 35 mg/dL (>40)",
         {"TEST_NAME": "HDL Cholesterol", "VALUE": "35 mg/dL", "REFERENCE_RANGE": "(>40)"}),

    make("Vitamin D 18 ng/mL (30-100)",
         {"TEST_NAME": "Vitamin D", "VALUE": "18 ng/mL", "REFERENCE_RANGE": "(30-100)"}),

    make("Vitamin D 45 ng/mL (30-100)",
         {"TEST_NAME": "Vitamin D", "VALUE": "45 ng/mL", "REFERENCE_RANGE": "(30-100)"}),

    make("TSH 5.5 µIU/mL (0.4-4.0)",
         {"TEST_NAME": "TSH", "VALUE": "5.5 µIU/mL", "REFERENCE_RANGE": "(0.4-4.0)"}),

    make("Creatinine 1.0 mg/dL (0.6-1.2)",
         {"TEST_NAME": "Creatinine", "VALUE": "1.0 mg/dL", "REFERENCE_RANGE": "(0.6-1.2)"}),

    make("Serum Iron 45 µg/dL (60-170)",
         {"TEST_NAME": "Serum Iron", "VALUE": "45 µg/dL", "REFERENCE_RANGE": "(60-170)"}),

    make("Urea 25 mg/dL (7-20)",
         {"TEST_NAME": "Urea", "VALUE": "25 mg/dL", "REFERENCE_RANGE": "(7-20)"}),

    make("Bilirubin Total 0.8 mg/dL (0.1-1.2)",
         {"TEST_NAME": "Bilirubin Total", "VALUE": "0.8 mg/dL", "REFERENCE_RANGE": "(0.1-1.2)"}),

    make("ALT 50 U/L (7-56)",
         {"TEST_NAME": "ALT", "VALUE": "50 U/L", "REFERENCE_RANGE": "(7-56)"}),

    make("AST 38 U/L (10-40)",
         {"TEST_NAME": "AST", "VALUE": "38 U/L", "REFERENCE_RANGE": "(10-40)"}),

    make("T3 1.2 ng/mL (0.8-1.8)",
         {"TEST_NAME": "T3", "VALUE": "1.2 ng/mL", "REFERENCE_RANGE": "(0.8-1.8)"}),

    make("T4 9.0 µg/dL (4.5-11.7)",
         {"TEST_NAME": "T4", "VALUE": "9.0 µg/dL", "REFERENCE_RANGE": "(4.5-11.7)"}),

    make("Vitamin B12 300 pg/mL (200-900)",
         {"TEST_NAME": "Vitamin B12", "VALUE": "300 pg/mL", "REFERENCE_RANGE": "(200-900)"}),

    make("Total Cholesterol 210 mg/dL (<200)",
         {"TEST_NAME": "Total Cholesterol", "VALUE": "210 mg/dL", "REFERENCE_RANGE": "(<200)"}),
]

print("Loaded test samples:", len(TEST_DATA))
