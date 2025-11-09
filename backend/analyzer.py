import pandas as pd
import re

# ✅ --- UPGRADED KNOWLEDGE BASE OF STANDARD RANGES ---
STANDARD_RANGES = {
    # CBC
    'HEMOGLOBIN': (13.5, 17.5),
    'RBC': (4.5, 5.9),
    'WBC': (4500, 11000),
    'PLATELET': (150000, 450000),
    'HEMATOCRIT': (38, 50),
    'MCV': (80, 100),
    'MCH': (27, 31),
    'MCHC': (32, 36),
    'RDW': (11.5, 14.5),
    'LYMPHOCYTES': (20, 40),
    'NEUTROPHILS': (50, 70),
    'MONOCYTES': (2, 8),

    # Lipids
    'TOTAL CHOLESTEROL': ('<', 200),
    'LDL CHOLESTEROL': ('<', 100),
    'HDL CHOLESTEROL': ('>', 40),
    'TRIGLYCERIDES': ('<', 150),

    # Metabolic
    'GLUCOSE': (70, 100),
    'HBA1C': ('<', 5.7),
    'CREATININE': (0.6, 1.2),
    'UREA': (7, 20),
    'SODIUM': (136, 146),
    'POTASSIUM': (3.5, 5.0),

    # Liver
    'ALT': (7, 56),
    'AST': (10, 40),
    'BILIRUBIN': (0.1, 1.2),

    # Thyroid
    'TSH': (0.4, 4.0),
    'T3': (0.8, 1.8),
    'T4': (4.5, 11.7),

    # Vitamins & Iron
    'VITAMIN B12': (200, 900),
    'VITAMIN D': (30, 100),
    'SERUM IRON': (60, 170),
}


# 🧠 --- FRIENDLY CLASSIFICATION LOGIC ---
def classify_result(value, low, high):
    """
    Classifies test results with soft labels like:
    Slightly Low / Moderately High / Severely High / Normal
    """
    if value < low:
        deviation = (low - value) / low
        if deviation < 0.1:
            return "Slightly Low"
        elif deviation < 0.25:
            return "Moderately Low"
        else:
            return "Severely Low"

    elif value > high:
        deviation = (value - high) / high
        if deviation < 0.1:
            return "Slightly High"
        elif deviation < 0.25:
            return "Moderately High"
        else:
            return "Severely High"

    else:
        return "Normal"


# 🩺 --- MAIN ANALYSIS FUNCTION ---
def analyze_results(df):
    """
    Analyzes the DataFrame using a hybrid approach:
    1. Tries to use the range from the report.
    2. Falls back to our STANDARD_RANGES knowledge base.
    3. Adds friendly soft-classification labels.
    """
    if df.empty:
        return df

    statuses = []
    used_ranges = []

    for _, row in df.iterrows():
        status = "Normal"
        used_range_str = "N/A"

        try:
            value = float(row["Value"])
            range_from_report = row.get("Reference Range")

            # --- CASE 1: Use range directly from report ---
            if pd.notna(range_from_report):
                used_range_str = str(range_from_report)
                numbers = re.findall(r"[\d\.]+", used_range_str)

                if len(numbers) >= 2:
                    low, high = float(numbers[0]), float(numbers[-1])
                    status = classify_result(value, low, high)

                elif len(numbers) == 1:
                    limit = float(numbers[0])
                    if "<" in used_range_str and value >= limit:
                        status = "Slightly High"
                    elif ">" in used_range_str and value <= limit:
                        status = "Slightly Low"

            # --- CASE 2: Use STANDARD_RANGES fallback ---
            else:
                test_name_upper = str(row["Test Name"]).upper()
                matched_key = next((key for key in STANDARD_RANGES if key in test_name_upper), None)

                if matched_key:
                    standard_range = STANDARD_RANGES[matched_key]

                    if isinstance(standard_range[0], str):
                        limit = standard_range[1]
                        used_range_str = f"{standard_range[0]} {limit} (Standard)"

                        if standard_range[0] == "<" and value >= limit:
                            status = "Slightly High"
                        elif standard_range[0] == ">" and value <= limit:
                            status = "Slightly Low"

                    else:
                        low, high = standard_range
                        used_range_str = f"{low} - {high} (Standard)"
                        status = classify_result(value, low, high)
                else:
                    status = "No Range Found"

        except (ValueError, TypeError):
            status = "Invalid Value"

        statuses.append(status)
        used_ranges.append(used_range_str)

    df["Status"] = statuses
    df["Reference Range Used"] = used_ranges
    return df
