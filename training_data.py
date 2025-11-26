# training_data.py
# -------------------------------------------
# PROGRAMMATIC TRAIN_DATA GENERATOR (300 -> 1000 samples)
# Generates many realistic, messy variations for robust NER training.
# Keeps offsets safe via normalize_spaces + make().
# -------------------------------------------

import re
import random
from copy import deepcopy

random.seed(12345)  # deterministic for reproducibility

# ------------------------------
# helper: normalize + make
# ------------------------------
def normalize_spaces(text):
    """Converts multiple spaces to a single space."""
    return re.sub(r"\s+", " ", text).strip()


def make(text, labels):
    """
    Auto-calculates correct entity offsets even if spacing changes.
    labels example:
    {"TEST_NAME": "Hemoglobin", "VALUE": "13.5 g/dL", "REFERENCE_RANGE": "(13.0-17.0)"}
    """
    clean_text = normalize_spaces(text)
    entities = []

    for label, substring in labels.items():
        if substring is None:
            continue

        clean_sub = normalize_spaces(substring)

        start = clean_text.find(clean_sub)
        if start == -1:
            # helpful error for debugging; rarely happens with our generator
            raise ValueError(f"ERROR: '{clean_sub}' not found in '{clean_text}'")

        end = start + len(clean_sub)
        entities.append((start, end, label))

    return (clean_text, {"entities": entities})


# ------------------------------
# Base canonical records (name, alt_names, canonical value, unit, reference)
# We will programmatically create many noisy variations of each record.
# ------------------------------
BASE_RECORDS = [
    # CBC
    {"name": "Hemoglobin", "alts": ["Hemoglobin", "Hb", "HGB"], "value": 13.5, "unit": "g/dL", "ref": "(13.0-17.0)"},
    {"name": "Hemoglobin", "alts": ["Hemoglobin", "Hb", "HGB"], "value": 11.2, "unit": "g/dL", "ref": "(12.0-16.0)"},
    {"name": "WBC Count", "alts": ["WBC Count", "WBC", "White Blood Cells"], "value": 7800, "unit": "/µL", "ref": "(4500-11000)"},
    {"name": "WBC Count", "alts": ["WBC Count", "WBC", "White Blood Cells"], "value": 15000, "unit": "/µL", "ref": "(4500-11000)"},
    {"name": "Platelet Count", "alts": ["Platelet Count", "Platelets"], "value": 250000, "unit": "/µL", "ref": "(150000-450000)"},
    {"name": "Platelet Count", "alts": ["Platelet Count", "Platelets"], "value": 490000, "unit": "/µL", "ref": "(150000-450000)"},
    {"name": "RBC Count", "alts": ["RBC Count", "RBC", "Red Blood Cells"], "value": 4.9, "unit": "mill/cmm", "ref": "(4.5-5.9)"},
    {"name": "Hematocrit", "alts": ["Hematocrit", "Hct"], "value": 42, "unit": "%", "ref": "(38-50)"},
    {"name": "MCV", "alts": ["MCV"], "value": 88, "unit": "fL", "ref": "(80-100)"},
    {"name": "MCH", "alts": ["MCH"], "value": 29, "unit": "pg", "ref": "(27-31)"},
    {"name": "MCHC", "alts": ["MCHC"], "value": 33, "unit": "g/dL", "ref": "(32-36)"},
    {"name": "RDW", "alts": ["RDW"], "value": 13, "unit": "%", "ref": "(11.5-14.5)"},
    {"name": "Neutrophils", "alts": ["Neutrophils", "Neut"], "value": 65, "unit": "%", "ref": "(50-70)"},
    {"name": "Lymphocytes", "alts": ["Lymphocytes", "Lymph"], "value": 32, "unit": "%", "ref": "(20-40)"},
    {"name": "Monocytes", "alts": ["Monocytes", "Mono"], "value": 6, "unit": "%", "ref": "(2-8)"},

    # Lipid profile
    {"name": "Total Cholesterol", "alts": ["Total Cholesterol", "Cholesterol"], "value": 180, "unit": "mg/dL", "ref": "(<200)"},
    {"name": "Total Cholesterol", "alts": ["Total Cholesterol", "Cholesterol"], "value": 220, "unit": "mg/dL", "ref": "(<200)"},
    {"name": "LDL Cholesterol", "alts": ["LDL Cholesterol", "LDL", "LDL-C"], "value": 98, "unit": "mg/dL", "ref": "(<100)"},
    {"name": "LDL Cholesterol", "alts": ["LDL Cholesterol", "LDL", "LDL-C"], "value": 160, "unit": "mg/dL", "ref": "(<100)"},
    {"name": "HDL Cholesterol", "alts": ["HDL Cholesterol", "HDL"], "value": 48, "unit": "mg/dL", "ref": "(>40)"},
    {"name": "Triglycerides", "alts": ["Triglycerides", "TG"], "value": 140, "unit": "mg/dL", "ref": "(<150)"},
    {"name": "Triglycerides", "alts": ["Triglycerides", "TG"], "value": 200, "unit": "mg/dL", "ref": "(<150)"},
    {"name": "VLDL", "alts": ["VLDL"], "value": 22, "unit": "mg/dL", "ref": "(10-40)"},

    # Liver
    {"name": "ALT", "alts": ["ALT", "SGPT"], "value": 55, "unit": "U/L", "ref": "(7-56)"},
    {"name": "ALT", "alts": ["ALT", "SGPT"], "value": 34, "unit": "U/L", "ref": "(7-56)"},
    {"name": "AST", "alts": ["AST", "SGOT"], "value": 44, "unit": "U/L", "ref": "(10-40)"},
    {"name": "Bilirubin Total", "alts": ["Bilirubin Total", "Bilirubin"], "value": 0.9, "unit": "mg/dL", "ref": "(0.1-1.2)"},
    {"name": "Alkaline Phosphatase", "alts": ["Alkaline Phosphatase", "ALP"], "value": 110, "unit": "U/L", "ref": "(44-147)"},

    # Kidney
    {"name": "Creatinine", "alts": ["Creatinine"], "value": 1.0, "unit": "mg/dL", "ref": "(0.6-1.2)"},
    {"name": "Creatinine", "alts": ["Creatinine"], "value": 1.6, "unit": "mg/dL", "ref": "(0.6-1.2)"},
    {"name": "Urea", "alts": ["Urea"], "value": 22, "unit": "mg/dL", "ref": "(7-20)"},
    {"name": "Blood Urea Nitrogen", "alts": ["Blood Urea Nitrogen", "BUN"], "value": 14, "unit": "mg/dL", "ref": "(7-20)"},

    # Thyroid
    {"name": "TSH", "alts": ["TSH"], "value": 3.2, "unit": "µIU/mL", "ref": "(0.4-4.0)"},
    {"name": "TSH", "alts": ["TSH"], "value": 6.1, "unit": "µIU/mL", "ref": "(0.4-4.0)"},
    {"name": "T3", "alts": ["T3"], "value": 1.1, "unit": "ng/mL", "ref": "(0.8-1.8)"},
    {"name": "T4", "alts": ["T4"], "value": 9.2, "unit": "µg/dL", "ref": "(4.5-11.7)"},

    # Vitamins & Iron
    {"name": "Vitamin B12", "alts": ["Vitamin B12", "B12"], "value": 220, "unit": "pg/mL", "ref": "(200-900)"},
    {"name": "Vitamin D", "alts": ["Vitamin D", "Vit D"], "value": 18, "unit": "ng/mL", "ref": "(30-100)"},
    {"name": "Serum Iron", "alts": ["Serum Iron"], "value": 45, "unit": "µg/dL", "ref": "(60-170)"},

    # Diagnosis-only (kept simple)
    {"name": "Diagnosis: Mild anemia.", "alts": ["Diagnosis: Mild anemia.", "Diagnosis - Mild anemia."], "value": None, "unit": None, "ref": None},
    {"name": "Diagnosis: Borderline hypothyroidism.", "alts": ["Diagnosis: Borderline hypothyroidism."], "value": None, "unit": None, "ref": None},
    {"name": "Diagnosis: Vitamin D deficiency.", "alts": ["Diagnosis: Vitamin D deficiency."], "value": None, "unit": None, "ref": None},
]

# ------------------------------
# Variation generators
# ------------------------------
SEPARATORS = [" ", " : ", " - ", " -  ", ": ", " - ", " — ", " :  ", "  "]
PAREN_VARIANTS = ["({r})", " ({r})", " {r}", " [{r}]", "({r}) "]
UNIT_VARIANTS = {
    "g/dL": ["g/dL", "g/dl", "gm/dL", "gm/dl"],
    "/µL": ["/µL", "/uL", "/µl", "/u l"],
    "mg/dL": ["mg/dL", "mg/dl", "mg per dL", " mg/dL"],
    "U/L": ["U/L", "U L", "U per L"],
    "%": ["%", " percent", "%"],
    "mill/cmm": ["mill/cmm", "mill/cmm", "mill/cmm"],
    "pg/mL": ["pg/mL", "pg/ml"],
    "ng/mL": ["ng/mL", "ng/ml"],
    "µg/dL": ["µg/dL", "ug/dL", "µg/dl"],
    "µIU/mL": ["µIU/mL", "uIU/mL", "µIU/ml"]
}

def format_value(val, unit):
    """Return textual representations: integer, decimal, with commas, scientific sometimes."""
    if val is None:
        return ""
    # choose representation
    if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
        v_int = int(round(val))
        reps = [str(v_int), f"{v_int:,}"]
    else:
        reps = [str(val), f"{val:.1f}", f"{val:.2f}"]
    # occasionally produce scientific notation for large ints (rare)
    if random.random() < 0.02 and float(val) >= 10000:
        reps.append("{:.2e}".format(float(val)))
    return random.choice(reps)


def assemble_text(name_variant, value_text, unit_variant, range_text, pattern_style=0):
    """
    Combine parts into a line with various noisy patterns.
    pattern_style chooses between different formatting patterns.
    """
    # common paddings
    sep = random.choice(SEPARATORS)
    # some patterns put unit immediately after value, some with space
    if unit_variant:
        # join val + unit with or without space
        if random.random() < 0.5:
            val_unit = f"{value_text} {unit_variant}"
        else:
            val_unit = f"{value_text}{unit_variant}"
    else:
        val_unit = value_text

    patterns = [
        f"{name_variant}{sep}{val_unit} {range_text if range_text else ''}",
        f"{name_variant}{sep}{val_unit} {range_text if range_text else ''}",
        f"{name_variant} {val_unit} {range_text if range_text else ''}",
        f"{name_variant}:{val_unit} {range_text if range_text else ''}",
        f"{name_variant} - {val_unit} {range_text if range_text else ''}",
        f"{name_variant} .... {val_unit} {range_text if range_text else ''}",
        f"{name_variant}  {val_unit}  {range_text if range_text else ''}",
        f"{name_variant} {val_unit}  {range_text if range_text else ''}"
    ]
    # random case transform sometimes
    text = random.choice(patterns)
    if random.random() < 0.15:
        text = text.upper()
    if random.random() < 0.12:
        text = text.lower()
    # insert random extra spaces occasionally
    if random.random() < 0.15:
        text = text.replace(" ", "  ")
    return text.strip()


# ------------------------------
# Build TRAIN_DATA
# ------------------------------
TARGET_COUNT = 1000  # total samples desired
TRAIN_DATA = []

# Start by seeding with clean canonical examples (one per BASE item)
for rec in BASE_RECORDS:
    name = rec["name"]
    # canonical value string
    if rec["value"] is None:
        text = rec["alts"][0]
        labels = {"TEST_NAME": rec["alts"][0]}
    else:
        unit_choice = UNIT_VARIANTS.get(rec["unit"], [rec["unit"]]) if rec["unit"] else [""]
        unit_variant = random.choice(unit_choice)
        value_text = format_value(rec["value"], rec["unit"])
        range_text = rec["ref"] or ""
        text = f"{rec['alts'][0]} {value_text} {unit_variant} {range_text}".strip()
        labels = {"TEST_NAME": rec["alts"][0], "VALUE": f"{value_text} {unit_variant}".strip(), "REFERENCE_RANGE": (range_text or "")}
    TRAIN_DATA.append(make(text, labels))

# Now create many noisy variations until we reach TARGET_COUNT
attempts = 0
max_attempts = TARGET_COUNT * 5

while len(TRAIN_DATA) < TARGET_COUNT and attempts < max_attempts:
    attempts += 1
    rec = random.choice(BASE_RECORDS)
    # select name variant
    name_variant = random.choice(rec["alts"])
    # choose unit variant
    unit_variant = None
    if rec["unit"]:
        unit_choices = UNIT_VARIANTS.get(rec["unit"], [rec["unit"]])
        unit_variant = random.choice(unit_choices)
    # produce value text
    value_text = format_value(rec["value"], rec["unit"]) if rec["value"] is not None else ""
    # produce range text using random parenthesis variants
    range_text = ""
    if rec["ref"]:
        # normalize reference like "(13.0-17.0)" into inner "13.0-17.0"
        inner = rec["ref"].strip()
        inner = inner.replace("(", "").replace(")", "")
        # sometimes add spaces or different punctuation
        if random.random() < 0.25:
            inner = inner.replace("-", " - ")
        if random.random() < 0.1:
            inner = inner.replace("-", "–")  # en dash variation
        range_template = random.choice(PAREN_VARIANTS)
        range_text = range_template.format(r=inner)
    # build messy name variants: add abbreviations, units inline, weird hyphens
    # sometimes prepend or append extra notes
    name_noise = name_variant
    if random.random() < 0.12:
        # common lab abbreviations
        name_noise = name_noise.replace("Count", "").strip()
    if random.random() < 0.12:
        # add small label like "Ref"
        if random.random() < 0.5:
            name_noise = f"{name_noise} -"
        else:
            name_noise = f"{name_noise}:"
    if random.random() < 0.08:
        name_noise = name_noise + " (report)"
    # assemble final text
    text = assemble_text(name_noise, value_text, unit_variant, range_text)
    # ensure labels match substrings we inserted: create label substrings that appear in normalize_spaces(text)
    # For TEST_NAME label we use the exact name_variant (without noise punctuation) if possible
    test_name_label = name_variant
    # For VALUE label we need the exact value+unit substring as it appears; find it
    val_unit_candidate = f"{value_text} {unit_variant}".strip() if unit_variant else value_text
    # In some noisy cases val and unit may be concatenated without space; add that possibility
    val_unit_candidate_no_space = f"{value_text}{unit_variant}".strip() if unit_variant else value_text

    # Choose which form exists in text
    normalized_text = normalize_spaces(text)
    chosen_value_label = None
    if val_unit_candidate and normalize_spaces(val_unit_candidate) in normalized_text:
        chosen_value_label = normalize_spaces(val_unit_candidate)
    elif val_unit_candidate_no_space and normalize_spaces(val_unit_candidate_no_space) in normalized_text:
        chosen_value_label = normalize_spaces(val_unit_candidate_no_space)
    else:
        # Sometimes value shows alone (no unit)
        if value_text and normalize_spaces(value_text) in normalized_text:
            chosen_value_label = normalize_spaces(value_text)
        else:
            chosen_value_label = None

    # Reference range substring selection
    chosen_ref_label = None
    if range_text:
        if normalize_spaces(range_text) in normalized_text:
            chosen_ref_label = normalize_spaces(range_text)
        else:
            # try with simple parentheses
            simple = f"({inner})" if rec.get("ref") else ""
            if simple and simple in normalized_text:
                chosen_ref_label = simple

    # Build labels dict safely
    labels = {}
    labels["TEST_NAME"] = test_name_label
    if chosen_value_label:
        labels["VALUE"] = chosen_value_label
    if chosen_ref_label:
        labels["REFERENCE_RANGE"] = chosen_ref_label

    # Some records are diagnosis-only (no VALUE); allow that
    try:
        TRAIN_DATA.append(make(text, labels))
    except Exception:
        # skip problematic variants and continue
        continue

# final check: if we still haven't reached TARGET_COUNT, fill with more clean canonical repeats
while len(TRAIN_DATA) < TARGET_COUNT:
    rec = random.choice(BASE_RECORDS)
    if rec["value"] is None:
        text = rec["alts"][0]
        labels = {"TEST_NAME": rec["alts"][0]}
    else:
        unit_choice = UNIT_VARIANTS.get(rec["unit"], [rec["unit"]]) if rec["unit"] else [""]
        unit_variant = random.choice(unit_choice)
        value_text = format_value(rec["value"], rec["unit"])
        range_text = rec["ref"] or ""
        text = f"{rec['alts'][0]} {value_text} {unit_variant} {range_text}".strip()
        labels = {"TEST_NAME": rec["alts"][0], "VALUE": f"{value_text} {unit_variant}".strip(), "REFERENCE_RANGE": (range_text or "")}
    TRAIN_DATA.append(make(text, labels))

print("Generated TRAIN_DATA with", len(TRAIN_DATA), "samples (target:", TARGET_COUNT, ")")
