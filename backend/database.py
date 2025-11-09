# backend/database.py
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Setup the local SQLite DB ---
DB_FILE = os.environ.get("LAB_APP_DB", "instance.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# --- Define Tables ---
class ReportRecord(Base):
    __tablename__ = "report_records"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), index=True)  # email or typed username
    test_name = Column(String(255))
    value = Column(Float)
    status = Column(String(50))
    diagnosis = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    filename = Column(String(255), nullable=True)


def init_db():
    """Creates the table if it doesn't exist."""
    Base.metadata.create_all(bind=engine)


# --- Save report data ---
def save_report_to_db(username: str, analyzed_df: pd.DataFrame, diagnosis: str = None, filename: str = None):
    """
    Saves each test from the analyzed DataFrame into the database,
    linked to the username and current date.
    """
    init_db()
    session = SessionLocal()
    try:
        upload_date = datetime.utcnow()

        # Ensure the expected columns exist
        if not all(col in analyzed_df.columns for col in ["Test Name", "Value", "Status"]):
            raise ValueError("Analyzed DataFrame must contain 'Test Name', 'Value', and 'Status' columns.")

        for _, row in analyzed_df.iterrows():
            rec = ReportRecord(
                username=username,
                test_name=str(row["Test Name"]),
                value=float(row["Value"]),
                status=str(row["Status"]),
                diagnosis=diagnosis,
                upload_date=upload_date,
                filename=filename
            )
            session.add(rec)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# --- Fetch user history ---
def get_user_history(username: str) -> pd.DataFrame:
    """
    Returns a DataFrame of all past reports for the given username.
    Columns: test_name, value, status, upload_date
    """
    init_db()
    session = SessionLocal()
    try:
        records = session.query(ReportRecord).filter_by(username=username).order_by(ReportRecord.upload_date).all()
        if not records:
            return pd.DataFrame()

        data = [{
            "test_name": r.test_name,
            "value": r.value,
            "status": r.status,
            "upload_date": r.upload_date
        } for r in records]

        return pd.DataFrame(data)
    finally:
        session.close()
