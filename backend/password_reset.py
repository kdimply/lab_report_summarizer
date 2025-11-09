import secrets
import time
from .db import SessionLocal
from .models import User
from .auth import hash_password

# Temporary in-memory storage for reset codes
RESET_CODES = {}

def request_password_reset(email: str):
    """Generates a temporary reset code for a user email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "No account found with this email."

        reset_code = secrets.token_hex(4).upper()  # e.g., "A4F93D2B"
        RESET_CODES[reset_code] = {"email": email, "created_at": time.time()}

        # ✅ Instead of printing, we return the code to show directly in Streamlit
        return True, f"🔐 Your password reset code is: **{reset_code}**\n\nUse this code below to reset your password. (Expires in 15 minutes.)"
    finally:
        db.close()



def reset_password(code: str, new_password: str):
    """Validates reset code and updates user password."""
    if code not in RESET_CODES:
        return False, "Invalid or expired reset code."

    record = RESET_CODES[code]
    if time.time() - record["created_at"] > 900:  # 15 min expiry
        del RESET_CODES[code]
        return False, "Reset code expired. Please request a new one."

    email = record["email"]
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "User not found."

        hashed = hash_password(new_password)
        user.password_hash = hashed
        db.commit()

        del RESET_CODES[code]
        return True, "✅ Password has been successfully reset! You can now log in with your new password."
    finally:
        db.close()
