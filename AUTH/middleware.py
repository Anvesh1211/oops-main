"""
AUTH Middleware — JWT verification and role-based access control decorators.
Protects routes by verifying tokens and checking user permissions.
"""

from functools import wraps
from flask import request, jsonify, g
from AUTH.utils import decode_token
from AUTH.models import get_user_by_id


def get_token_from_request():
    """Extract JWT token from Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None


def verify_token(f):
    """
    Decorator to verify JWT token on protected routes.
    Sets g.current_user with user data if token is valid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({
                "status": "error",
                "message": "Access denied. No token provided."
            }), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({
                "status": "error",
                "message": "Invalid token."
            }), 401

        if "error" in payload:
            return jsonify({
                "status": "error",
                "message": payload["error"]
            }), 401

        # Verify token type
        if payload.get("type") != "access":
            return jsonify({
                "status": "error",
                "message": "Invalid token type."
            }), 401

        # Get user from database
        user = get_user_by_id(payload.get("user_id"))
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 401

        if not user.get("is_active"):
            return jsonify({
                "status": "error",
                "message": "Account is deactivated."
            }), 403

        # Set current user in Flask's g object
        g.current_user = user
        g.token_payload = payload

        return f(*args, **kwargs)
    return decorated


def check_role(*allowed_roles):
    """
    Decorator factory for role-based access control.
    Usage: @check_role("faculty") or @check_role("student", "faculty")
    Must be used AFTER @verify_token.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return jsonify({
                    "status": "error",
                    "message": "Authentication required."
                }), 401

            user_role = g.current_user.get("role", "")
            if user_role not in allowed_roles:
                return jsonify({
                    "status": "error",
                    "message": f"Access denied. Required role: {', '.join(allowed_roles)}. Your role: {user_role}."
                }), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
