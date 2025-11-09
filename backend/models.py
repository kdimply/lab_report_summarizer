# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {"id": self.id, "email": self.email, "full_name": self.full_name, "created_at": self.created_at}

# Optional placeholder for reports (we'll use this in Step 2)
class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_date = Column(DateTime(timezone=True), server_default=func.now())  # date when user uploaded
    filename = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)  # short text summary
    raw_json = Column(Text, nullable=True)  # serialized parsed results
