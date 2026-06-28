"""
AUTH Utilities — Password hashing, JWT token management, input validation.
Core security utilities for the ResourcePro authentication system.
"""

import re
import os
import secrets
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = 60  # minutes
REFRESH_TOKEN_EXPIRY = 7  # days


# ─── PASSWORD HASHING ────────────────────────────────────────────────
def hash_password(password):
    """Hash a password using bcrypt with auto-generated salt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# ─── JWT TOKEN MANAGEMENT ────────────────────────────────────────────
def generate_access_token(user_id, role):
    """Generate a JWT access token with user_id and role."""
    payload = {
        "user_id": user_id,
        "role": role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRY),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user_id):
    """Generate a long-lived refresh token."""
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRY),
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),  # unique ID to allow revocation
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def generate_reset_token():
    """Generate a secure random token for password resets."""
    return secrets.token_urlsafe(48)


# ─── INPUT VALIDATION ────────────────────────────────────────────────
def validate_email(email):
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    if len(email) > 255:
        return False, "Email too long"
    return True, None


def validate_password(password):
    """
    Validate password strength.
    Requirements: 8+ chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char.
    Returns (is_valid, error_message).
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password too long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        return False, "Password must contain at least one special character"
    return True, None


def validate_name(name):
    """Validate name. Returns (is_valid, error_message)."""
    if not name or not isinstance(name, str):
        return False, "Name is required"
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 100:
        return False, "Name too long"
    if not re.match(r'^[a-zA-Z\s\.\-\']+$', name):
        return False, "Name contains invalid characters"
    return True, None


def validate_role(role):
    """Validate role. Returns (is_valid, error_message)."""
    valid_roles = ['student', 'faculty']
    if not role or role.lower() not in valid_roles:
        return False, f"Role must be one of: {', '.join(valid_roles)}"
    return True, None


def sanitize_input(text):
    """Sanitize input to prevent XSS and injection attacks."""
    if not text:
        return text
    # Remove potentially dangerous characters
    text = str(text).strip()
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#x27;')
    return text
