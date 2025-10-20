# backend/analyzer.py

import pandas as pd
import re

# ✅ --- UPGRADED KNOWLEDGE BASE OF STANDARD RANGES ---
# This version includes more detailed CBC components and other common tests.
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

def analyze_results(df):
    """
    Analyzes the DataFrame using a hybrid approach:
    1. Tries to use the range from the report.
    2. Falls back to our STANDARD_RANGES knowledge base.
    """
    if df.empty:
        return df

    statuses = []
    used_ranges = []

    for _, row in df.iterrows():
        status = 'Normal'
        used_range_str = "N/A"

        try:
            value = float(row['Value'])
            range_from_report = row.get('Reference Range')

            if pd.notna(range_from_report):
                used_range_str = str(range_from_report)
                numbers = re.findall(r"[\d\.]+", used_range_str)
                if len(numbers) >= 2:
                    low, high = float(numbers[0]), float(numbers[-1])
                    if value < low: status = 'Low'
                    elif value > high: status = 'High'
                elif len(numbers) == 1:
                    limit = float(numbers[0])
                    if '<' in used_range_str and value >= limit: status = 'High'
                    if '>' in used_range_str and value <= limit: status = 'Low'
            else:
                test_name_upper = str(row['Test Name']).upper()
                matched_key = next((key for key in STANDARD_RANGES if key in test_name_upper), None)
                
                if matched_key:
                    standard_range = STANDARD_RANGES[matched_key]
                    if isinstance(standard_range[0], str): # Handle '<' or '>' ranges
                        limit = standard_range[1]
                        used_range_str = f"{standard_range[0]} {limit} (Standard)"
                        if standard_range[0] == '<' and value >= limit: status = 'High'
                        if standard_range[0] == '>' and value <= limit: status = 'Low'
                    else: # Handle (low, high) ranges
                        low, high = standard_range
                        used_range_str = f"{low} - {high} (Standard)"
                        if value < low: status = 'Low'
                        elif value > high: status = 'High'
                else:
                    status = 'No Range Found'
        except (ValueError, TypeError):
            status = 'Invalid Value'
        
        statuses.append(status)
        used_ranges.append(used_range_str)

    df['Status'] = statuses
    df['Reference Range Used'] = used_ranges
    return df