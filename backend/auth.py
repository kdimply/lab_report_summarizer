# backend/auth.py
import os
import hashlib
from datetime import datetime
from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError
from pymongo import MongoClient

# ---------- MongoDB Connection ----------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://dimply:Dimply2004@lab-cluster.csxjcka.mongodb.net/?retryWrites=true&w=majority"
)

client = MongoClient(MONGO_URI)
db = client["lab_report_db"]
users_col = db["users"]

# ---------- Password Hashing ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Pre-hash using SHA256 → bcrypt (fixes 72-byte bcrypt limit)."""
    if not password:
        raise ValueError("Password cannot be empty.")

    sha_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(sha_hash)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify SHA256-prehashed password."""
    if not plain:
        return False
    sha_hash = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    return pwd_context.verify(sha_hash, hashed)


# ---------- AGE CALCULATOR ----------
def calculate_age(dob_str: str):
    """Calculates age from DOB (format YYYY-MM-DD)."""
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )
    except:
        return None


# ---------- CREATE USER ----------
def create_user(email: str, password: str, full_name: str = None, dob: str = None):
    """Creates user with full name + DOB + auto age calculation."""
    # Validate email
    try:
        v = validate_email(email)
        email = v.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {e}")

    # Check if email already exists
    if users_col.find_one({"email": email}):
        raise ValueError("Email already registered.")

    # Hash password
    hashed = hash_password(password)

    # Age
    age = calculate_age(dob) if dob else None

    user_doc = {
        "email": email,
        "password_hash": hashed,
        "full_name": full_name.strip() if full_name else "Not Provided",
        "dob": dob if dob else None,
        "age": age,
        "created_at": datetime.utcnow()
    }

    users_col.insert_one(user_doc)

    # DO NOT return password hash to session
    user_doc.pop("password_hash", None)

    return user_doc


# ---------- AUTHENTICATE ----------
def authenticate_user(email: str, password: str):
    """Returns user document if password matches, else None."""
    user = users_col.find_one({"email": email})
    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    # remove hash before sending to session
    safe_user = {
        "email": user["email"],
        "full_name": user.get("full_name", "Not Provided"),
        "dob": user.get("dob"),
        "age": user.get("age")
    }
    return safe_user


# ---------- GET USER ----------
def get_user_by_email(email: str):
    user = users_col.find_one({"email": email})
    if not user:
        return None

    # clean return
    user.pop("password_hash", None)
    return user
