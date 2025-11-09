import pandas as pd

# ✅ Expert knowledge base (same as before)
EXPERT_KNOWLEDGE_BASE = {
    "HEMOGLOBIN": {"PlainName": "Hemoglobin (Oxygen Carrier)", "WhatItIs": "Carries oxygen in your red blood cells.",
        "Low": {"Meaning": "Low hemoglobin can indicate anemia, which may cause tiredness and weakness.",
                "FoodDirections": "Try eating iron-rich foods like **spinach, lentils, red meat**, and **fortified cereals**. Pair them with Vitamin C (like oranges) for better absorption."},
        "High": {"Meaning": "High hemoglobin can happen with dehydration or increased red blood cell production.",
                 "FoodDirections": "Stay hydrated and maintain a balanced diet."}},
    "PLATELET": {"PlainName": "Platelets (Clotting Cells)", "WhatItIs": "Help your blood to clot when you get a cut.",
        "Low": {"Meaning": "Low platelets may cause easy bruising or slow healing.",
                "FoodDirections": "Eat foods rich in **Vitamin K, B12, and Folate** like leafy greens, eggs, and citrus fruits."},
        "High": {"Meaning": "High platelets can slightly raise clotting risk.",
                 "FoodDirections": "Add anti-inflammatory foods like **ginger, garlic, and turmeric**."}},
    "WBC": {"PlainName": "White Blood Cells (Immune Cells)", "WhatItIs": "Fight infections in your body.",
        "High": {"Meaning": "High WBC may mean your body is fighting an infection or inflammation.",
                 "FoodDirections": "Support immunity with **berries, citrus fruits, and green tea**."},
        "Low": {"Meaning": "Low WBC weakens your immunity, making you more prone to infections.",
                "FoodDirections": "Eat protein-rich foods with Zinc and Vitamin C — like **beans, nuts, and chicken**."}},
    "CHOLESTEROL": {"PlainName": "Total Cholesterol", "WhatItIs": "Measures all cholesterol types in your blood.",
        "High": {"Meaning": "Slightly high cholesterol can mean an imbalance in fats, often diet-related.",
                 "FoodDirections": "Eat more fiber (like oats, apples) and healthy fats (avocado, nuts). Limit fried foods."}},
    "LDL": {"PlainName": "LDL ('Bad' Cholesterol)", "WhatItIs": "Can build up in arteries if too high.",
        "High": {"Meaning": "High LDL increases heart risk over time.",
                 "FoodDirections": "Avoid fried or processed foods; add **oats, barley, and fish** to your meals."}},
    "HDL": {"PlainName": "HDL ('Good' Cholesterol)", "WhatItIs": "Helps remove bad cholesterol.",
        "Low": {"Meaning": "Low HDL slightly raises heart risk.",
                "FoodDirections": "Boost healthy fats (olive oil, avocados, nuts) and regular physical activity."}},
    "GLUCOSE": {"PlainName": "Blood Sugar", "WhatItIs": "Measures sugar in your blood.",
        "High": {"Meaning": "High glucose might suggest your body isn’t processing sugar efficiently.",
                 "FoodDirections": "Avoid sugary drinks; focus on **fiber-rich foods** like veggies and whole grains."}},
    "CREATININE": {"PlainName": "Creatinine (Kidney Marker)", "WhatItIs": "A waste product filtered by kidneys.",
        "High": {"Meaning": "High creatinine may show your kidneys are working extra hard.",
                 "FoodDirections": "Stay hydrated and reduce red meat."}},
    "TSH": {"PlainName": "Thyroid Stimulating Hormone", "WhatItIs": "Controls thyroid activity.",
        "High": {"Meaning": "High TSH can mean your thyroid is underactive (hypothyroidism).",
                 "FoodDirections": "Add iodine and selenium from **iodized salt, seafood, and Brazil nuts**."}},
}

# 🩺 --- FRIENDLY SUMMARY GENERATOR ---
def generate_summary(analyzed_df, diagnosis):
    """
    Generates a calm, human-style summary with friendly tone and clear ranges.
    Perfect for normal users — easy to read, positive, and reassuring.
    """

    abnormal_results = analyzed_df[
        analyzed_df["Status"].isin([
            "Slightly Low", "Low", "Severely Low",
            "Slightly High", "High", "Severely High", "Moderately High"
        ])
    ].copy()

    # 🌿 All values normal
    if abnormal_results.empty and not diagnosis:
        return (
            "## 🌿 Everything Looks Great!\n\n"
            "All your test results are within the healthy range — that means your body is in great balance. "
            "Keep up your daily habits like hydration, movement, and good nutrition. 💚"
        )

    summary = "## 🩺 Understanding Your Report\n\n"

    if diagnosis:
        summary += f"**AI Observation:** {diagnosis}\n\n"

    # Separate into groups
    low_vals = abnormal_results[abnormal_results["Status"].str.contains("Low", case=False)]
    high_vals = abnormal_results[abnormal_results["Status"].str.contains("High", case=False)]

    # 🩸 Lower-side readings
    if not low_vals.empty:
        summary += "### ⬇️ Some readings are a little below the ideal range\n"
        for _, row in low_vals.iterrows():
            name = row["Test Name"].title()
            summary += (
                f"**{name}:** {row['Value']} _(Normal: {row['Reference Range Used']})_\n"
                "This usually isn’t a big concern — it may reflect fatigue, hydration levels, or nutrition gaps. "
                "Make sure you’re eating enough iron, protein, and vitamins to support your body’s balance. 🌸\n\n"
            )

    # 💧 Higher-side readings
    if not high_vals.empty:
        summary += "### ⬆️ A few results are slightly higher than expected\n"
        for _, row in high_vals.iterrows():
            name = row["Test Name"].title()
            summary += (
                f"**{name}:** {row['Value']} _(Normal: {row['Reference Range Used']})_\n"
                "A mild increase like this is very common — often due to a recent meal, mild stress, or dehydration. "
                "Drinking water, light exercise, and balanced food can easily bring it back into range. ☀️\n\n"
            )

    # 💬 Final wrap-up
    summary += (
        "---\n"
        "✅ **Overall Summary:** Your report looks mostly healthy. "
        "Small shifts like these are usually temporary and don’t indicate illness. "
        "Keep focusing on daily balance — fresh meals, sleep, movement, and water — the basics that keep you glowing and strong. 💖\n\n"
        "💡 *Tip:* Recheck in a few months or after small lifestyle tweaks to see your progress!"
    )

    return summary




# 🔗 --- HEALTH CONNECTIONS LOGIC ---
CONNECTIONS_KNOWLEDGE_BASE = {
    "Possible Iron Deficiency Anemia": {
        "required": [("HEMOGLOBIN", "Low"), ("MCV", "Low")],
        "Insight": "Low Hemoglobin and Low MCV suggest **Iron Deficiency Anemia** — a common, fixable cause of fatigue. Try iron-rich foods and talk to your doctor for confirmation."
    },
    "Signs of Metabolic Stress": {
        "required": [("GLUCOSE", "High"), ("TRIGLYCERIDES", "High")],
        "Insight": "High Glucose and Triglycerides may indicate **Metabolic Stress**. Balanced meals, fiber, and regular exercise can help stabilize levels."
    },
}

def find_possible_connections(analyzed_df):
    """Finds connected test patterns and returns insights."""
    insights = []
    abnormal_results = analyzed_df[
        ~analyzed_df["Status"].str.contains("Normal", case=False, na=False)
    ]

    for connection, rules in CONNECTIONS_KNOWLEDGE_BASE.items():
        all_met = True
        for test, expected in rules["required"]:
            matched = any(
                (test in str(name).upper()) and (expected.lower() in str(stat).lower())
                for name, stat in zip(abnormal_results["Test Name"], abnormal_results["Status"])
            )
            if not matched:
                all_met = False
                break

        if all_met:
            insights.append(rules["Insight"])

    return insights
