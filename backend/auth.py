import hashlib
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError

from .db import SessionLocal
from .models import User


# --- Password hashing ---
def hash_password(password: str) -> str:
    """
    Safe hashing with SHA256 prehash (removes 72-byte limit).
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    
    sha_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return bcrypt.using(rounds=12).hash(sha_hash)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verifies password using the same SHA256 prehashing.
    """
    if not plain:
        return False

    sha_hash = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    return bcrypt.verify(sha_hash, hashed)


# --- User management functions ---
def create_user(email: str, password: str, full_name: str = None):
    """Creates a new user after validating email and password."""
    try:
        v = validate_email(email)
        email = v.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {e}")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already registered.")

        hashed = hash_password(password)
        user = User(email=email, password_hash=hashed, full_name=full_name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def authenticate_user(email: str, password: str):
    """Return user if credentials are correct, else None."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    finally:
        db.close()


def get_user_by_id(user_id: int):
    """Get user record by ID."""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()
