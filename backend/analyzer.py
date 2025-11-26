# analyzer.py (updated)
import pandas as pd
import re

STANDARD_RANGES = {
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
    'TOTAL CHOLESTEROL': ('<', 200),
    'LDL CHOLESTEROL': ('<', 100),
    'HDL CHOLESTEROL': ('>', 40),
    'TRIGLYCERIDES': ('<', 150),
    'GLUCOSE': (70, 100),
    'HBA1C': ('<', 5.7),
    'CREATININE': (0.6, 1.2),
    'UREA': (7, 20),
    'SODIUM': (136, 146),
    'POTASSIUM': (3.5, 5.0),
    'ALT': (7, 56),
    'AST': (10, 40),
    'BILIRUBIN': (0.1, 1.2),
    'TSH': (0.4, 4.0),
    'T3': (0.8, 1.8),
    'T4': (4.5, 11.7),
    'VITAMIN B12': (200, 900),
    'VITAMIN D': (30, 100),
    'SERUM IRON': (60, 170),
}

def classify_result(value, low, high):
    if low is None and high is not None:
        if value >= high:
            return "Slightly High" if (value - high) / max(high, 1e-6) < 0.1 else "High"
        return "Normal"

    if high is None and low is not None:
        if value <= low:
            return "Slightly Low" if (low - value) / max(low, 1e-6) < 0.1 else "Low"
        return "Normal"

    if low is not None and high is not None:
        if value < low:
            d = (low - value) / max(low, 1e-6)
            if d < 0.1:
                return "Slightly Low"
            if d < 0.25:
                return "Moderately Low"
            return "Severely Low"
        if value > high:
            d = (value - high) / max(high, 1e-6)
            if d < 0.1:
                return "Slightly High"
            if d < 0.25:
                return "Moderately High"
            return "Severely High"
        return "Normal"

    return "No Range Found"

def analyze_results(df):
    if df is None or df.empty:
        if df is None:
            df = pd.DataFrame()
        df["Status"] = []
        df["Reference Range Used"] = []
        return df

    statuses = []
    used_ranges = []

    for _, row in df.iterrows():
        test_name = str(row.get("Test Name", "")).strip().upper()
        raw_val = row.get("Value", None)
        parsed_range = row.get("Reference Range Parsed", None)
        raw_range_text = row.get("Reference Range Raw", "")

        try:
            value = float(raw_val)
        except Exception:
            statuses.append("Invalid Value")
            used_ranges.append("N/A")
            continue

        status = "Normal"
        used_range_label = "N/A"

        # Prefer report-parsed range
        if parsed_range:
            low, high, comp = parsed_range
            status = classify_result(value, low, high)
            if low is not None and high is not None:
                used_range_label = f"{low} - {high} (Report)"
            elif comp == '<' or (comp is None and low is None and high is not None):
                used_range_label = f"< {high} (Report)"
            elif comp == '>' or (comp is None and low is not None and high is None):
                used_range_label = f"> {low} (Report)"
            else:
                used_range_label = raw_range_text or "Report Range"
        else:
            # fallback to STANDARD_RANGES
            matched = None
            for key in STANDARD_RANGES:
                if key in test_name:
                    matched = key
                    break

            if matched:
                std = STANDARD_RANGES[matched]
                if isinstance(std[0], str):
                    op, limit = std
                    used_range_label = f"{op} {limit} (Standard)"
                    if op == '<':
                        status = "Slightly High" if value >= limit else "Normal"
                    else:
                        status = "Slightly Low" if value <= limit else "Normal"
                else:
                    low, high = std
                    used_range_label = f"{low} - {high} (Standard)"
                    status = classify_result(value, low, high)
            else:
                status = "No Range Found"
                used_range_label = "N/A"

        statuses.append(status)
        used_ranges.append(used_range_label)

    df["Status"] = statuses
    df["Reference Range Used"] = used_ranges
    return df
