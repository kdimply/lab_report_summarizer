# training_data.py

# Our final, "Advanced" dataset with over 35 examples.
# This version includes multi-line formats to build our most robust model.

TRAIN_DATA = [
    # --- Set 1: Various CBC Formats (including multi-line) ---
    ("Test Name Result Normal Range Units Hemoglobin 12.1 11.0-16.0 g/dL WBC 6.7 4.5-11.0 10^3/uL",
     {"entities": [(36, 46, "TEST_NAME"), (47, 51, "VALUE"), (52, 61, "REFERENCE_RANGE"), (67, 70, "TEST_NAME"), (71, 74, "VALUE"), (75, 83, "REFERENCE_RANGE")]}),
    ("CBC Results: Hemoglobin 10.5 g/dL (13.5-17.5), Hematocrit 32 % (38-50)",
     {"entities": [(13, 23, "TEST_NAME"), (24, 28, "VALUE"), (35, 45, "REFERENCE_RANGE"), (48, 58, "TEST_NAME"), (59, 61, "VALUE"), (65, 70, "REFERENCE_RANGE")]}),
    ("White Blood Cell Count\nResult: 15.2 (4.5-11.0)",
     {"entities": [(0, 22, "TEST_NAME"), (31, 35, "VALUE"), (37, 45, "REFERENCE_RANGE")]}),
    ("Red Blood Cell Count 5.8 4.50-5.90",
     {"entities": [(0, 20, "TEST_NAME"), (21, 24, "VALUE"), (25, 34, "REFERENCE_RANGE")]}),
    ("Hemoglobin: 9.8 g/dL", {"entities": [(0, 10, "TEST_NAME"), (12, 18, "VALUE")]}),
    ("WBC Count: 11,000 /cmm", {"entities": [(0, 9, "TEST_NAME"), (11, 22, "VALUE")]}),
    ("Diagnosis: Mild anemia with leukocytosis.", {"entities": [(11, 46, "DIAGNOSIS")]}),

    # --- Set 2: Various Lipid & Cholesterol Formats ---
    ("LIPID PROFILE: Total Cholesterol 245 mg/dL <200, LDL Cholesterol 160 mg/dL <100",
     {"entities": [(16, 33, "TEST_NAME"), (34, 37, "VALUE"), (44, 48, "REFERENCE_RANGE"), (50, 65, "TEST_NAME"), (66, 69, "VALUE"), (76, 80, "REFERENCE_RANGE")]}),
    ("Test: Total Cholesterol, Value: 210, Range: <200",
     {"entities": [(6, 23, "TEST_NAME"), (32, 35, "VALUE"), (44, 48, "REFERENCE_RANGE")]}),
    ("HDL Cholesterol: 65 mg/dL, Normal: >40",
     {"entities": [(0, 15, "TEST_NAME"), (17, 19, "VALUE"), (36, 39, "REFERENCE_RANGE")]}),
    ("TRIGLYCERIDES\n190 mg/dl (50-150)",
     {"entities": [(0, 13, "TEST_NAME"), (14, 17, "VALUE"), (25, 32, "REFERENCE_RANGE")]}),
    ("Diagnosis: Normal lipid profile.", {"entities": [(11, 36, "DIAGNOSIS")]}),

    # --- Set 3: Various Metabolic, Liver & Kidney Formats ---
    ("Creatinine\n1.4 mg/dL\nRef: 0.6-1.2",
     {"entities": [(0, 10, "TEST_NAME"), (11, 14, "VALUE"), (26, 33, "REFERENCE_RANGE")]}),
    ("Blood Sugar (Fasting): 135 mg/dL", {"entities": [(0, 22, "TEST_NAME"), (24, 32, "VALUE")]}),
    ("HbA1c: 7.2%", {"entities": [(0, 5, "TEST_NAME"), (7, 11, "VALUE")]}),
    ("Diagnosis: Indicates Type 2 Diabetes.", {"entities": [(11, 39, "DIAGNOSIS")]}),
    ("Sodium 135 mEq/L 136-146. Potassium 3.4 mEq/L 3.5-5.0",
     {"entities": [(0, 6, "TEST_NAME"), (7, 10, "VALUE"), (18, 25, "REFERENCE_RANGE"), (27, 36, "TEST_NAME"), (37, 40, "VALUE"), (48, 55, "REFERENCE_RANGE")]}),
    ("Liver Panel: ALT 55 U/L (7-56), AST 45 U/L (10-40)",
     {"entities": [(13, 16, "TEST_NAME"), (17, 19, "VALUE"), (24, 29, "REFERENCE_RANGE"), (32, 35, "TEST_NAME"), (36, 38, "VALUE"), (43, 49, "REFERENCE_RANGE")]}),
    ("ALANINE AMINOTRANSFERASE (ALT) 62 10-50 U/L",
     {"entities": [(0, 30, "TEST_NAME"), (31, 33, "VALUE"), (34, 39, "REFERENCE_RANGE")]}),
    ("Bilirubin: 0.9 mg/dL", {"entities": [(0, 9, "TEST_NAME"), (11, 19, "VALUE")]}),

    # --- Set 4: Various Thyroid, Vitamin & Iron Formats ---
    ("Thyroid Stimulating Hormone (TSH)\n5.1 uIU/mL (Normal 0.4-4.0)",
     {"entities": [(0, 31, "TEST_NAME"), (32, 35, "VALUE"), (49, 56, "REFERENCE_RANGE")]}),
    ("TSH: 5.8 µIU/mL", {"entities": [(0, 3, "TEST_NAME"), (5, 14, "VALUE")]}),
    ("T3: 1.2 ng/mL", {"entities": [(0, 2, "TEST_NAME"), (4, 12, "VALUE")]}),
    ("Diagnosis: Borderline hypothyroidism.", {"entities": [(11, 40, "DIAGNOSIS")]}),
    ("Vitamin B12: 220 pg/mL", {"entities": [(0, 11, "TEST_NAME"), (13, 21, "VALUE")]}),
    ("Vitamin D3: 15 ng/mL", {"entities": [(0, 10, "TEST_NAME"), (12, 19, "VALUE")]}),
    ("Diagnosis: Vitamin D deficiency detected.", {"entities": [(11, 47, "DIAGNOSIS")]}),
    ("Serum Iron\nResult: 50 ug/dL",
     {"entities": [(0, 10, "TEST_NAME"), (19, 21, "VALUE")]}),
    ("Diagnosis: Mild iron deficiency anemia.", {"entities": [(11, 45, "DIAGNOSIS")]}),

    # --- Set 5: Different Layouts & Edge Cases ---
    ("Test: Platelets, Value: 460, Range: 150-450",
     {"entities": [(6, 15, "TEST_NAME"), (24, 27, "VALUE"), (36, 43, "REFERENCE_RANGE")]}),
    ("LYMPHOCYTES % 25 20-40",
     {"entities": [(0, 12, "TEST_NAME"), (15, 17, "VALUE"), (18, 23, "REFERENCE_RANGE")]}),
    ("Neutrophils\nValue: 75 %\nRange: 50-70",
     {"entities": [(0, 11, "TEST_NAME"), (19, 21, "VALUE"), (31, 36, "REFERENCE_RANGE")]}),
    ("Investigation Result Unit Normal Value\nHEMOGLOBIN 15.1 gm/dl 13.0-18.0",
     {"entities": [(40, 50, "TEST_NAME"), (51, 55, "VALUE"), (62, 71, "REFERENCE_RANGE")]}),
    ("Monocytes 9 % (2-8)",
     {"entities": [(0, 9, "TEST_NAME"), (10, 11, "VALUE"), (15, 18, "REFERENCE_RANGE")]}),
]