"""
AUTH Routes — Flask Blueprint for all authentication API endpoints.
Defines REST API routes for register, login, profile, password reset, etc.
"""

from flask import Blueprint, request, jsonify, g
from AUTH.controllers import (
    register_user, login_user, get_profile, get_activity_log,
    refresh_access_token, logout_user, request_password_reset,
    reset_password, list_users
)
from AUTH.middleware import verify_token, check_role


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ─── PUBLIC ROUTES ────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (student or faculty)."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body is required"}), 400

    ip_address = request.remote_addr
    response, status_code = register_user(data, ip_address)
    return jsonify(response), status_code


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body is required"}), 400

    ip_address = request.remote_addr
    response, status_code = login_user(data, ip_address)
    return jsonify(response), status_code


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body is required"}), 400

    refresh_token = data.get('refresh_token', '')
    response, status_code = refresh_access_token(refresh_token)
    return jsonify(response), status_code


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request a password reset token."""
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({"status": "error", "message": "Email is required"}), 400

    response, status_code = request_password_reset(data['email'])
    return jsonify(response), status_code


@auth_bp.route('/reset-password', methods=['POST'])
def reset_pwd():
    """Reset password with a valid reset token."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body is required"}), 400

    token = data.get('token', '')
    new_password = data.get('new_password', '')

    if not token or not new_password:
        return jsonify({"status": "error", "message": "Token and new password are required"}), 400

    response, status_code = reset_password(token, new_password)
    return jsonify(response), status_code


# ─── PROTECTED ROUTES ─────────────────────────────────────────────────

@auth_bp.route('/profile', methods=['GET'])
@verify_token
def profile():
    """Get current user's profile (protected)."""
    response, status_code = get_profile(g.current_user['id'])
    return jsonify(response), status_code


@auth_bp.route('/activity', methods=['GET'])
@verify_token
def activity():
    """Get current user's activity log (protected)."""
    limit = request.args.get('limit', 50, type=int)
    response, status_code = get_activity_log(g.current_user['id'], limit)
    return jsonify(response), status_code


@auth_bp.route('/logout', methods=['POST'])
@verify_token
def logout():
    """Logout and invalidate session (protected)."""
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token', '')
    ip_address = request.remote_addr
    response, status_code = logout_user(g.current_user['id'], refresh_token, ip_address)
    return jsonify(response), status_code


# ─── ROLE-PROTECTED ROUTES ────────────────────────────────────────────

@auth_bp.route('/users', methods=['GET'])
@verify_token
@check_role('faculty', 'admin')
def users():
    """List all users (faculty/admin only)."""
    role_filter = request.args.get('role')
    response, status_code = list_users(role_filter)
    return jsonify(response), status_code


@auth_bp.route('/student/dashboard-data', methods=['GET'])
@verify_token
@check_role('student', 'admin')
def student_dashboard_data():
    """Get student-specific dashboard data (student only)."""
    user = g.current_user
    return jsonify({
        "status": "success",
        "dashboard": {
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            },
            "permissions": [
                "view_resources",
                "download_materials",
                "book_rooms",
                "view_schedule"
            ]
        }
    }), 200


@auth_bp.route('/faculty/dashboard-data', methods=['GET'])
@verify_token
@check_role('faculty', 'admin')
def faculty_dashboard_data():
    """Get faculty-specific dashboard data (faculty only)."""
    user = g.current_user
    return jsonify({
        "status": "success",
        "dashboard": {
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            },
            "permissions": [
                "upload_resources",
                "manage_content",
                "view_student_usage",
                "approve_bookings",
                "reject_bookings",
                "view_analytics"
            ]
        }
    }), 200
