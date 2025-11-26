# backend/database.py
import os
from datetime import datetime
import pandas as pd
from pymongo import MongoClient

# ---------------- MONGO CONNECTION ----------------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://dimply:Dimply2004@lab-cluster.csxjcka.mongodb.net/?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["lab_report_db"]
reports_col = db["reports"]


# ------------------------------------------------------------
# SAVE — FULL REPORT (for Upload Page)
# ------------------------------------------------------------
def save_full_report_to_db(username, analyzed_df, summary, diagnosis, raw_text, chart_path, filename):
    """
    Saves EVERYTHING into MongoDB:
      - username
      - test results
      - summary
      - diagnosis
      - raw extracted text
      - chart (base64 image)
      - filename
      - upload timestamp
    """

    # Convert tests to list of objects
    tests = []
    for _, row in analyzed_df.iterrows():
        tests.append({
            "test_name": row["Test Name"],
            "value": float(row["Value"]),
            "status": row["Status"]
        })

    # Convert chart → base64 (optional)
    chart_base64 = None
    if chart_path:
        try:
            with open(chart_path, "rb") as img_file:
                import base64
                chart_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        except:
            chart_base64 = None

    # Build document
    doc = {
        "username": username,
        "upload_date": datetime.utcnow(),
        "filename": filename,
        "summary": summary,
        "diagnosis": diagnosis,
        "raw_text": raw_text,
        "tests": tests,
        "chart_b64": chart_base64
    }

    # Insert into MongoDB
    try:
        reports_col.insert_one(doc)
    except Exception as e:
        raise RuntimeError(f"Error saving report: {e}")


# ------------------------------------------------------------
# HISTORY — RETURN ALL REPORTS
# ------------------------------------------------------------
def get_user_history(username):
    try:
        history = list(
            reports_col.find({"username": username}, {"_id": 0})
                        .sort("upload_date", 1)
        )
        return history
    except Exception as e:
        raise RuntimeError(f"Error fetching history: {e}")


# ------------------------------------------------------------
# LAST TWO — FOR COMPARISON
# ------------------------------------------------------------
def get_last_two_reports(username):
    try:
        last_two = list(
            reports_col.find({"username": username}, {"_id": 0})
                        .sort("upload_date", -1)
                        .limit(2)
        )
        return last_two
    except Exception as e:
        raise RuntimeError(f"Error fetching comparison reports: {e}")
