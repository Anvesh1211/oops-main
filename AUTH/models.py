"""
AUTH Models — Database schema and user model for ResourcePro authentication.
Handles user table creation, CRUD operations, and activity logging.
"""

import sqlite3
import os
from datetime import datetime


DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DATABASE")
DB_PATH = os.path.join(DB_DIR, "db.sqlite3")


def get_auth_connection():
    """Get a connection to the auth database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_auth_db():
    """Initialize the authentication database tables."""
    conn = get_auth_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'admin')),
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # Activity logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Password reset tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Sessions table for "remember me" feature
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            refresh_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_valid INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[AUTH DB] Authentication tables initialized")


def create_user(name, email, password_hash, role):
    """Create a new user. Returns user dict or None if email exists."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "name": name, "email": email, "role": role}
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_email(email):
    """Get a user by email address."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, name, email, password, role, is_active, created_at, last_login FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    """Get a user by ID."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, name, email, role, is_active, created_at, last_login FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_last_login(user_id):
    """Update user's last login timestamp."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET last_login = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()


def update_user_password(user_id, new_password_hash):
    """Update a user's password."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ?, updated_at = ? WHERE id = ?",
        (new_password_hash, datetime.utcnow().isoformat(), user_id)
    )
    conn.commit()
    conn.close()


def log_activity(user_id, action, details=None, ip_address=None):
    """Log a user activity for audit trail."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
        (user_id, action, details, ip_address)
    )
    conn.commit()
    conn.close()


def get_user_activity(user_id, limit=50):
    """Get activity logs for a user."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT action, details, ip_address, created_at FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def store_reset_token(user_id, token, expires_at):
    """Store a password reset token."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at)
    )
    conn.commit()
    conn.close()


def validate_reset_token(token):
    """Validate a password reset token. Returns user_id or None."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT user_id, expires_at FROM password_reset_tokens WHERE token = ? AND used = 0",
        (token,)
    ).fetchone()
    conn.close()
    if row:
        expires = row['expires_at']
        # Strip timezone info for naive comparison
        exp_dt = datetime.fromisoformat(expires.replace('+00:00', '').replace('Z', ''))
        if exp_dt > datetime.utcnow():
            return row['user_id']
    return None


def mark_reset_token_used(token):
    """Mark a reset token as used."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def store_session(user_id, refresh_token, expires_at):
    """Store a refresh session for remember me."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sessions (user_id, refresh_token, expires_at) VALUES (?, ?, ?)",
        (user_id, refresh_token, expires_at)
    )
    conn.commit()
    conn.close()


def validate_session(refresh_token):
    """Validate a refresh token session. Returns user_id or None."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT user_id, expires_at FROM sessions WHERE refresh_token = ? AND is_valid = 1",
        (refresh_token,)
    ).fetchone()
    conn.close()
    if row:
        expires = row['expires_at']
        exp_dt = datetime.fromisoformat(expires.replace('+00:00', '').replace('Z', ''))
        if exp_dt > datetime.utcnow():
            return row['user_id']
    return None


def invalidate_session(refresh_token):
    """Invalidate a refresh token session."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET is_valid = 0 WHERE refresh_token = ?", (refresh_token,))
    conn.commit()
    conn.close()


def invalidate_all_sessions(user_id):
    """Invalidate all sessions for a user (e.g., on password change)."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET is_valid = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_users(role=None):
    """Get all users, optionally filtered by role."""
    conn = get_auth_connection()
    cursor = conn.cursor()
    if role:
        rows = cursor.execute(
            "SELECT id, name, email, role, is_active, created_at, last_login FROM users WHERE role = ? ORDER BY created_at DESC",
            (role,)
        ).fetchall()
    else:
        rows = cursor.execute(
            "SELECT id, name, email, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize tables on import
init_auth_db()
