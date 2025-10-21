# backend/summarizer.py

# Our definitive "expert knowledge base" for providing helpful interpretations and advice.
EXPERT_KNOWLEDGE_BASE = {
    "HEMOGLOBIN": {"PlainName": "Hemoglobin (Oxygen Carrier)", "WhatItIs": "The protein in your red blood cells that carries oxygen from your lungs to the rest of your body.",
        "Low": {"Meaning": "Low hemoglobin is a primary sign of anemia, which can cause fatigue and weakness.", "FoodDirections": "Focus on iron-rich foods like **spinach, lentils, red meat, and fortified cereals**. Pairing these with Vitamin C (e.g., oranges) boosts iron absorption."},
        "High": {"Meaning": "High hemoglobin can be a sign of dehydration or conditions that cause your body to produce too many red blood cells.", "FoodDirections": "Focus on staying well-hydrated by drinking plenty of water."}},
    "PLATELET": {"PlainName": "Platelets (Clotting Cells)", "WhatItIs": "Tiny cells in your blood that form clots to stop bleeding.",
        "Low": {"Meaning": "Low platelets can lead to easy bruising or prolonged bleeding.", "FoodDirections": "Consume foods rich in Vitamin K, B12, and Folate, such as **leafy greens, eggs, and citrus fruits**."},
        "High": {"Meaning": "High platelets can increase the risk of unnecessary blood clotting.", "FoodDirections": "Incorporate foods with anti-inflammatory properties like **ginger, garlic, and turmeric**."}},
    "WBC": {"PlainName": "White Blood Cells (Immune Cells)", "WhatItIs": "The primary cells of your immune system, responsible for fighting infections.",
        "High": {"Meaning": "A high WBC count often indicates your body is fighting an infection or inflammation.", "FoodDirections": "Support your immune system with foods rich in antioxidants, like **berries, citrus fruits, and green tea**."},
        "Low": {"Meaning": "A low WBC count can weaken your immune system, making you more vulnerable to infections.", "FoodDirections": "Focus on a balanced diet rich in protein and vitamins (Zinc, Vitamin C) from **beans, nuts, and lean poultry**."}},
    "CHOLESTEROL": {"PlainName": "Total Cholesterol", "WhatItIs": "A measure of all the cholesterol in your blood, including 'good' and 'bad' types.",
        "High": {"Meaning": "High total cholesterol is a risk factor for heart disease.", "FoodDirections": "Reduce saturated fats. Eat more soluble fiber from **oats and apples**, and healthy fats from **avocados and nuts**."}},
    "LDL": {"PlainName": "LDL ('Bad' Cholesterol)", "WhatItIs": "The type of cholesterol that can build up in your arteries.",
        "High": {"Meaning": "High LDL is a strong indicator of an increased risk for heart attack and stroke.", "FoodDirections": "Crucially, avoid processed and fried foods. Increase your intake of **oats, barley, and fatty fish like salmon**."}},
    "HDL": {"PlainName": "HDL ('Good' Cholesterol)", "WhatItIs": "The 'good' cholesterol that helps remove bad cholesterol from your arteries.",
        "Low": {"Meaning": "Low HDL levels can increase your risk of heart disease.", "FoodDirections": "Increase intake of healthy fats from **olive oil, avocados, and nuts**. Regular exercise is also very effective."}},
    "GLUCOSE": {"PlainName": "Blood Glucose (Sugar)", "WhatItIs": "Measures the amount of sugar in your blood, used to monitor diabetes.",
        "High": {"Meaning": "High blood glucose can be a sign of pre-diabetes or diabetes.", "FoodDirections": "Avoid sugary drinks and refined carbs (white bread, pasta). Focus on **high-fiber foods like vegetables and whole grains**."}},
    "CREATININE": {"PlainName": "Creatinine (Kidney Marker)", "WhatItIs": "A waste product filtered by your kidneys.",
        "High": {"Meaning": "Elevated creatinine can indicate that your kidneys are not filtering waste effectively.", "FoodDirections": "Reduce intake of red meat. It's important to control blood pressure and stay hydrated with **water**."}},
    "TSH": {"PlainName": "TSH (Thyroid Hormone)", "WhatItIs": "This hormone regulates your thyroid gland.",
        "High": {"Meaning": "A high TSH level often indicates an underactive thyroid (hypothyroidism).", "FoodDirections": "Ensure adequate intake of iodine and selenium from sources like **iodized salt, seafood, and Brazil nuts**."}},
}

def generate_summary(analyzed_df, diagnosis):
    """Generates the full, detailed summary with explanations and food advice."""
    
    abnormal_results = analyzed_df[analyzed_df['Status'].isin(['Low', 'High'])].copy()

    if abnormal_results.empty and not diagnosis:
        return "## ✅ All Clear!\n\nAll extracted test results appear to be within the normal range. Continue maintaining a healthy lifestyle."

    summary = ""
    if diagnosis:
        summary += f"## 🩺 AI-Powered Summary\n\nBased on the report, the key finding appears to be: **{diagnosis}**\n\n"
    else:
        summary += "## 📝 Your Lab Report Summary\n\n"

    if not abnormal_results.empty:
        summary += "Here is a breakdown of your key results that are outside the normal range:\n"
        for _, row in abnormal_results.iterrows():
            test_name_upper = str(row['Test Name']).upper()
            status = row['Status']
            matched_key = next((key for key in EXPERT_KNOWLEDGE_BASE if key in test_name_upper), None)

            if matched_key:
                info = EXPERT_KNOWLEDGE_BASE[matched_key]
                summary += f"\n### ❗ {info['PlainName']}: Your level is **{status}**\n"
                summary += f"**Your Result:** {row['Value']} (Range: {row['Reference Range Used']})\n\n"
                if status in info:
                    summary += f"**- What this may mean:** {info[status]['Meaning']}\n"
                    if "FoodDirections" in info[status]:
                        summary += f"**- 🥦 Food Directions:** {info[status]['FoodDirections']}\n"
    
    summary += "\n---\n**Disclaimer:** This is an AI-generated summary for informational purposes only. Please consult with your doctor."
    return summary

# (Keep all your existing code in summarizer.py)
# Add this new code at the very bottom of the file:

CONNECTIONS_KNOWLEDGE_BASE = {
    "Possible Iron Deficiency Anemia": {
        "required": [("HEMOGLOBIN", "Low"), ("MCV", "Low")],
        "Insight": "Your report shows both **low Hemoglobin** and **low MCV** (an indicator of small red blood cells). This combination is often seen in cases of iron deficiency anemia. It would be a good idea to discuss this pattern with your doctor."
    },
    "Signs of Metabolic Stress": {
        "required": [("GLUCOSE", "High"), ("TRIGLYCERIDES", "High")],
        "Insight": "The combination of **high Blood Glucose** and **high Triglycerides** can be a sign of metabolic stress. Focusing on a diet low in sugar and refined carbs, along with regular exercise, is often recommended by health professionals."
    }
}

def find_possible_connections(analyzed_df):
    insights = []
    abnormal_results = analyzed_df[analyzed_df['Status'].isin(['Low', 'High'])]
    
    for connection, rules in CONNECTIONS_KNOWLEDGE_BASE.items():
        all_conditions_met = True
        for test, status in rules['required']:
            if not any((test in name.upper()) and (stat == status) for name, stat in zip(abnormal_results['Test Name'], abnormal_results['Status'])):
                all_conditions_met = False
                break
        
        if all_conditions_met:
            insights.append(rules['Insight'])
    
    return insights