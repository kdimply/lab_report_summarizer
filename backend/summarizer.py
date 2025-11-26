# summarizer.py (updated)
import pandas as pd

# -------------------------------------------------
#  SMALL, SIMPLE, SUPER-EASY EXPLANATIONS
# -------------------------------------------------
EXPERT_KNOWLEDGE_BASE = {
    "HEMOGLOBIN": {
        "Plain": "Hemoglobin (oxygen-carrying protein)",
        "Low": "Low hemoglobin usually means anemia — common and fixable.",
        "High": "High values may happen from dehydration or living at high altitude.",
        "FixLow": "Add iron-rich foods (spinach, eggs, dates, lentils) + Vitamin C foods.",
    },
    "WBC": {
        "Plain": "White Blood Cells (immunity cells)",
        "High": "Often means your body is fighting an infection.",
        "Low": "Low WBC can weaken immunity.",
        "FixLow": "Eat protein-rich foods, nuts, beans, and citrus fruits.",
    },
    "PLATELET": {
        "Plain": "Platelets (help blood clot)",
        "Low": "Can cause easy bruising.",
        "High": "May slightly increase clotting tendency.",
        "FixLow": "Include Vitamin B12 + folate foods like eggs and leafy greens.",
    },
    "GLUCOSE": {
        "Plain": "Blood Sugar",
        "High": "Can be due to sweets, stress, or poor sleep.",
        "FixHigh": "Avoid sugary drinks. Add fiber-rich foods and walk daily.",
    },
    "CHOLESTEROL": {
        "Plain": "Total Cholesterol",
        "High": "High cholesterol usually comes from diet or genetics.",
        "FixHigh": "Eat oats, apples, nuts. Reduce fried/packaged foods.",
    },
    "TSH": {
        "Plain": "Thyroid Hormone Controller",
        "High": "High TSH may point to low thyroid function.",
        "FixHigh": "Add iodine-rich foods (iodized salt, seafood).",
    }
}

# -------------------------------------------------
#  FRIENDLY SUMMARY GENERATOR
# -------------------------------------------------
def generate_summary(analyzed_df, diagnosis):
    """Creates an easy-to-read summary for users."""

    if analyzed_df is None or analyzed_df.empty:
        if diagnosis:
            return f"## 🩺 Quick Summary\n**Doctor’s Note / Observation:** {diagnosis}\n\nNo numeric values were extracted."
        return "## 🌿 No test values detected in the report."

    analyzed_df["Status"] = analyzed_df["Status"].astype(str)

    abnormal = analyzed_df[~analyzed_df["Status"].str.match(r'^\s*Normal\s*$', case=False, na=False)]

    if abnormal.empty and not diagnosis:
        return (
            "## 🌿 Your Health Looks Great!\n"
            "All your test values are within the healthy range. Keep drinking water, "
            "moving daily, and eating balanced meals 💚."
        )

    summary_lines = []

    if diagnosis:
        summary_lines.append(f"**Doctor’s Note / Observation:** {diagnosis}\n")

    summary_lines.append("Here’s what stood out in your report:\n")

    for _, row in abnormal.iterrows():
        name = str(row.get("Test Name", "")).title()
        value = row.get("Value", "")
        unit = row.get("Unit", "")
        status = row.get("Status", "")
        used_range = row.get("Reference Range Used", "N/A")

        summary_lines.append(f"### • {name} — {status}")
        val_display = f"{value} {unit}".strip()
        summary_lines.append(f"- **Your Value:** {val_display} (Normal: {used_range})")

        info = EXPERT_KNOWLEDGE_BASE.get(name.upper(), None)

        if info:
            if "High" in status:
                if "High" in info:
                    summary_lines.append(f"- **What This Means:** {info['High']}")
                if "FixHigh" in info:
                    summary_lines.append(f"- **What To Do:** {info['FixHigh']}")
            else:
                if "Low" in info:
                    summary_lines.append(f"- **What This Means:** {info['Low']}")
                if "FixLow" in info:
                    summary_lines.append(f"- **What To Do:** {info['FixLow']}")
        else:
            if "High" in status:
                summary_lines.append("- **Meaning:** Slightly high values can be due to meals, stress, or dehydration.")
                summary_lines.append("- **Tip:** Drink water, avoid heavy meals before testing.")
            else:
                summary_lines.append("- **Meaning:** Low values may reflect nutrition gaps or tiredness.")
                summary_lines.append("- **Tip:** Eat balanced meals and rest well.")

        summary_lines.append("")  # spacing

    # ----------------------- UPDATED PART (your requested line) -----------------------
    summary_lines.append(
        "---\n### ✅ Overall\n"
        "Nothing here looks scary — most numbers shift due to food, stress, water intake, or sleep. "
        "A few simple habits can balance your levels naturally.\n\n"
        "If you feel unwell, consider showing this report to your doctor. 💙\n\n"
        "⚠️ **Note:** This summary is for your information and understanding only. "
        "Always consult your doctor for medical advice."
    )
    # -------------------------------------------------------------------------------

    return "\n".join(summary_lines)

# -------------------------------------------------
#  CONNECTION PATTERNS
# -------------------------------------------------
CONNECTIONS_KNOWLEDGE_BASE = {
    "Iron Deficiency Pattern": {
        "need": [("HEMOGLOBIN", "Low"), ("MCV", "Low")],
        "msg": "Your Hemoglobin + MCV pattern suggests **possible iron deficiency**. Try iron-rich foods and retest in a few weeks."
    },
    "Blood Sugar Pattern": {
        "need": [("GLUCOSE", "High"), ("TRIGLYCERIDES", "High")],
        "msg": "High Glucose + Triglycerides together can indicate **metabolic stress**. Light exercise after meals helps."
    }
}

def find_possible_connections(analyzed_df):
    insights = []
    if analyzed_df is None or analyzed_df.empty:
        return insights

    abnormal = analyzed_df[~analyzed_df["Status"].str.match(r'^\s*Normal\s*$', case=False, na=False)]

    for label, rule in CONNECTIONS_KNOWLEDGE_BASE.items():
        found = True
        for test, cond in rule["need"]:
            match = abnormal[
                abnormal["Test Name"].str.contains(test, case=False, na=False)
                & abnormal["Status"].str.contains(cond, case=False, na=False)
            ]
            if match.empty:
                found = False
                break
        if found:
            insights.append(rule["msg"])

    return insights
