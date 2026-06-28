"""
AUTH Controllers — Business logic for authentication operations.
Handles registration, login, profile, password reset, and session management.
"""

from AUTH.models import (
    create_user, get_user_by_email, get_user_by_id,
    update_last_login, update_user_password, log_activity,
    get_user_activity, store_reset_token, validate_reset_token,
    mark_reset_token_used, store_session, validate_session,
    invalidate_session, invalidate_all_sessions, get_all_users
)
from AUTH.utils import (
    hash_password, verify_password, generate_access_token,
    generate_refresh_token, generate_reset_token, decode_token,
    validate_email, validate_password, validate_name, validate_role,
    sanitize_input
)
from datetime import datetime, timedelta, timezone


def register_user(data, ip_address=None):
    """
    Register a new user.
    Returns (response_dict, status_code).
    """
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', '').strip().lower()

    # Validate all inputs
    valid, err = validate_name(name)
    if not valid:
        return {"status": "error", "message": err}, 400

    valid, err = validate_email(email)
    if not valid:
        return {"status": "error", "message": err}, 400

    valid, err = validate_password(password)
    if not valid:
        return {"status": "error", "message": err}, 400

    valid, err = validate_role(role)
    if not valid:
        return {"status": "error", "message": err}, 400

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing:
        return {"status": "error", "message": "Email already registered"}, 409

    # Sanitize name
    name = sanitize_input(name)

    # Hash password and create user
    password_hash = hash_password(password)
    user = create_user(name, email, password_hash, role)

    if not user:
        return {"status": "error", "message": "Registration failed"}, 500

    # Log activity
    log_activity(user['id'], 'register', f"New {role} registration", ip_address)

    # Generate tokens
    access_token = generate_access_token(user['id'], user['role'])
    refresh_token = generate_refresh_token(user['id'])

    # Store session
    store_session(
        user['id'],
        refresh_token,
        (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    )

    return {
        "status": "success",
        "message": "Registration successful",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role']
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }, 201


def login_user(data, ip_address=None):
    """
    Authenticate a user and return tokens.
    Returns (response_dict, status_code).
    """
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)

    # Validate inputs
    if not email or not password:
        return {"status": "error", "message": "Email and password are required"}, 400

    valid, err = validate_email(email)
    if not valid:
        return {"status": "error", "message": err}, 400

    # Find user
    user = get_user_by_email(email)
    if not user:
        return {"status": "error", "message": "Invalid email or password"}, 401

    # Check if account is active
    if not user.get('is_active'):
        return {"status": "error", "message": "Account is deactivated"}, 403

    # Verify password
    if not verify_password(password, user['password']):
        log_activity(user['id'], 'login_failed', "Invalid password attempt", ip_address)
        return {"status": "error", "message": "Invalid email or password"}, 401

    # Update last login
    update_last_login(user['id'])

    # Log activity
    log_activity(user['id'], 'login', "Successful login", ip_address)

    # Generate tokens
    access_token = generate_access_token(user['id'], user['role'])
    refresh_token = generate_refresh_token(user['id'])

    # Store session with extended expiry if remember_me
    expiry_days = 30 if remember_me else 7
    store_session(
        user['id'],
        refresh_token,
        (datetime.now(timezone.utc) + timedelta(days=expiry_days)).isoformat()
    )

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role']
        },
        "access_token": access_token,
        "refresh_token": refresh_token
    }, 200


def get_profile(user_id):
    """
    Get user profile.
    Returns (response_dict, status_code).
    """
    user = get_user_by_id(user_id)
    if not user:
        return {"status": "error", "message": "User not found"}, 404

    return {
        "status": "success",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "created_at": user['created_at'],
            "last_login": user['last_login']
        }
    }, 200


def get_activity_log(user_id, limit=50):
    """
    Get activity logs for a user.
    Returns (response_dict, status_code).
    """
    activities = get_user_activity(user_id, limit)
    return {
        "status": "success",
        "activities": activities
    }, 200


def refresh_access_token(refresh_token_str):
    """
    Generate a new access token from a refresh token.
    Returns (response_dict, status_code).
    """
    if not refresh_token_str:
        return {"status": "error", "message": "Refresh token required"}, 400

    # Decode the refresh token
    payload = decode_token(refresh_token_str)
    if not payload or "error" in payload:
        return {"status": "error", "message": "Invalid or expired refresh token"}, 401

    if payload.get("type") != "refresh":
        return {"status": "error", "message": "Invalid token type"}, 401

    # Validate session in database
    user_id = validate_session(refresh_token_str)
    if not user_id:
        return {"status": "error", "message": "Session expired or invalidated"}, 401

    # Get user
    user = get_user_by_id(user_id)
    if not user:
        return {"status": "error", "message": "User not found"}, 404

    # Generate new access token
    new_access_token = generate_access_token(user['id'], user['role'])

    return {
        "status": "success",
        "access_token": new_access_token,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role']
        }
    }, 200


def logout_user(user_id, refresh_token_str=None, ip_address=None):
    """
    Logout user by invalidating their session.
    Returns (response_dict, status_code).
    """
    if refresh_token_str:
        invalidate_session(refresh_token_str)

    log_activity(user_id, 'logout', "User logged out", ip_address)

    return {
        "status": "success",
        "message": "Logged out successfully"
    }, 200


def request_password_reset(email):
    """
    Generate a password reset token.
    Returns (response_dict, status_code).
    """
    email = email.strip().lower()
    user = get_user_by_email(email)

    # Always return success to prevent email enumeration
    if not user:
        return {
            "status": "success",
            "message": "If the email exists, a reset link will be generated"
        }, 200

    token = generate_reset_token()
    expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    store_reset_token(user['id'], token, expires)

    log_activity(user['id'], 'password_reset_requested', "Reset token generated")

    return {
        "status": "success",
        "message": "If the email exists, a reset link will be generated",
        "reset_token": token  # In production, this would be emailed
    }, 200


def reset_password(token, new_password):
    """
    Reset password using a valid reset token.
    Returns (response_dict, status_code).
    """
    valid, err = validate_password(new_password)
    if not valid:
        return {"status": "error", "message": err}, 400

    user_id = validate_reset_token(token)
    if not user_id:
        return {"status": "error", "message": "Invalid or expired reset token"}, 400

    # Hash new password
    password_hash = hash_password(new_password)
    update_user_password(user_id, password_hash)

    # Mark token as used
    mark_reset_token_used(token)

    # Invalidate all existing sessions
    invalidate_all_sessions(user_id)

    log_activity(user_id, 'password_reset', "Password was reset")

    return {
        "status": "success",
        "message": "Password reset successful. Please login with your new password."
    }, 200


def list_users(role=None):
    """
    List all users (admin function).
    Returns (response_dict, status_code).
    """
    users = get_all_users(role)
    return {
        "status": "success",
        "users": users,
        "total": len(users)
    }, 200
