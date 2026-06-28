"""
AUTH Test Suite — Comprehensive tests for the ResourcePro authentication system.
Tests registration, login, token validation, RBAC, and security edge cases.
"""

import os
import sys
import json
import time

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Use a test database to avoid polluting real data
os.environ['JWT_SECRET'] = 'test-secret-key-for-testing-only'

from app import app

class AuthTestRunner:
    """Test runner for auth system."""

    def __init__(self):
        self.app = app
        self.client = app.test_client()
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.access_token_student = None
        self.access_token_faculty = None
        self.refresh_token_student = None

    def run_test(self, name, test_func):
        """Run a single test and track results."""
        try:
            result = test_func()
            if result:
                self.passed += 1
                print(f"  ✅ PASS: {name}")
            else:
                self.failed += 1
                self.errors.append(name)
                print(f"  ❌ FAIL: {name}")
        except Exception as e:
            self.failed += 1
            self.errors.append(f"{name} (Exception: {e})")
            print(f"  ❌ ERROR: {name} — {e}")

    def run_all(self):
        """Run the complete test suite."""
        print("\n" + "="*60)
        print("  🧪 ResourcePro Auth Test Suite")
        print("="*60 + "\n")

        # ─── Registration Tests ───────────────────────────────────
        print("📝 REGISTRATION TESTS")
        self.run_test("Register student with valid data", self.test_register_student)
        self.run_test("Register faculty with valid data", self.test_register_faculty)
        self.run_test("Reject duplicate email", self.test_register_duplicate_email)
        self.run_test("Reject weak password", self.test_register_weak_password)
        self.run_test("Reject invalid email format", self.test_register_invalid_email)
        self.run_test("Reject missing fields", self.test_register_missing_fields)
        self.run_test("Reject invalid role", self.test_register_invalid_role)
        print()

        # ─── Login Tests ──────────────────────────────────────────
        print("🔑 LOGIN TESTS")
        self.run_test("Login student successfully", self.test_login_student)
        self.run_test("Login faculty successfully", self.test_login_faculty)
        self.run_test("Login with wrong password fails", self.test_login_wrong_password)
        self.run_test("Login with nonexistent email fails", self.test_login_nonexistent)
        self.run_test("Login with empty body fails", self.test_login_empty)
        print()

        # ─── Protected Routes Tests ───────────────────────────────
        print("🔒 PROTECTED ROUTES TESTS")
        self.run_test("Access profile with valid token", self.test_profile_with_token)
        self.run_test("Access profile without token BLOCKED", self.test_profile_without_token)
        self.run_test("Access profile with invalid token BLOCKED", self.test_profile_invalid_token)
        self.run_test("Access profile with expired token format BLOCKED", self.test_profile_bad_token)
        print()

        # ─── RBAC Tests ───────────────────────────────────────────
        print("🎭 ROLE-BASED ACCESS TESTS")
        self.run_test("Student accessing student dashboard OK", self.test_student_dashboard_access)
        self.run_test("Student accessing faculty route BLOCKED", self.test_student_blocked_from_faculty)
        self.run_test("Faculty accessing faculty dashboard OK", self.test_faculty_dashboard_access)
        self.run_test("Faculty accessing user list OK", self.test_faculty_user_list)
        print()

        # ─── Token Refresh Tests ──────────────────────────────────
        print("🔄 TOKEN REFRESH TESTS")
        self.run_test("Refresh access token", self.test_token_refresh)
        self.run_test("Refresh with invalid token fails", self.test_invalid_refresh)
        print()

        # ─── Password Reset Tests ─────────────────────────────────
        print("🔐 PASSWORD RESET TESTS")
        self.run_test("Request password reset", self.test_forgot_password)
        self.run_test("Reset with invalid token fails", self.test_reset_invalid_token)
        print()

        # ─── Logout Test ─────────────────────────────────────────
        print("🚪 LOGOUT TESTS")
        self.run_test("Logout successfully", self.test_logout)
        print()

        # ─── Activity Log Test ────────────────────────────────────
        print("📋 ACTIVITY LOG TESTS")
        self.run_test("Activity log populated", self.test_activity_log)
        print()

        # ─── Security Tests ──────────────────────────────────────
        print("🛡️ SECURITY TESTS")
        self.run_test("SQL injection in email blocked", self.test_sql_injection)
        self.run_test("XSS in name sanitized", self.test_xss_sanitization)
        print()

        # ─── Summary ──────────────────────────────────────────────
        total = self.passed + self.failed
        print("="*60)
        print(f"  RESULTS: {self.passed}/{total} passed, {self.failed} failed")
        if self.errors:
            print(f"\n  Failed tests:")
            for err in self.errors:
                print(f"    ⚠ {err}")
        print("="*60 + "\n")

        return self.failed == 0

    # ═══════════════════════════════════════════════════════════════
    # TEST IMPLEMENTATIONS
    # ═══════════════════════════════════════════════════════════════

    def test_register_student(self):
        ts = str(int(time.time()))
        res = self.client.post('/api/auth/register', json={
            "name": "Test Student",
            "email": f"student_{ts}@test.edu",
            "password": "Test@1234",
            "role": "student"
        })
        data = res.get_json()
        if data['status'] == 'success' and res.status_code == 201:
            self.access_token_student = data['access_token']
            self.refresh_token_student = data['refresh_token']
            return True
        return False

    def test_register_faculty(self):
        ts = str(int(time.time()))
        res = self.client.post('/api/auth/register', json={
            "name": "Test Faculty",
            "email": f"faculty_{ts}@test.edu",
            "password": "Test@1234",
            "role": "faculty"
        })
        data = res.get_json()
        if data['status'] == 'success' and res.status_code == 201:
            self.access_token_faculty = data['access_token']
            return True
        return False

    def test_register_duplicate_email(self):
        email = "duplicate@test.edu"
        self.client.post('/api/auth/register', json={
            "name": "First User", "email": email, "password": "Test@1234", "role": "student"
        })
        res = self.client.post('/api/auth/register', json={
            "name": "Second User", "email": email, "password": "Test@5678", "role": "student"
        })
        return res.status_code == 409

    def test_register_weak_password(self):
        res = self.client.post('/api/auth/register', json={
            "name": "Weak Pass", "email": "weak@test.edu", "password": "123", "role": "student"
        })
        return res.status_code == 400

    def test_register_invalid_email(self):
        res = self.client.post('/api/auth/register', json={
            "name": "Bad Email", "email": "notanemail", "password": "Test@1234", "role": "student"
        })
        return res.status_code == 400

    def test_register_missing_fields(self):
        res = self.client.post('/api/auth/register', json={"name": "Missing"})
        return res.status_code == 400

    def test_register_invalid_role(self):
        res = self.client.post('/api/auth/register', json={
            "name": "Bad Role", "email": "role@test.edu", "password": "Test@1234", "role": "superadmin"
        })
        return res.status_code == 400

    def test_login_student(self):
        email = "login_test_s@test.edu"
        self.client.post('/api/auth/register', json={
            "name": "Login Student", "email": email, "password": "Test@1234", "role": "student"
        })
        res = self.client.post('/api/auth/login', json={"email": email, "password": "Test@1234"})
        data = res.get_json()
        if data['status'] == 'success':
            self.access_token_student = data['access_token']
            self.refresh_token_student = data.get('refresh_token')
            return True
        return False

    def test_login_faculty(self):
        email = "login_test_f@test.edu"
        self.client.post('/api/auth/register', json={
            "name": "Login Faculty", "email": email, "password": "Test@1234", "role": "faculty"
        })
        res = self.client.post('/api/auth/login', json={"email": email, "password": "Test@1234"})
        data = res.get_json()
        if data['status'] == 'success':
            self.access_token_faculty = data['access_token']
            return True
        return False

    def test_login_wrong_password(self):
        email = "wrong_pass@test.edu"
        self.client.post('/api/auth/register', json={
            "name": "Wrong Pass", "email": email, "password": "Test@1234", "role": "student"
        })
        res = self.client.post('/api/auth/login', json={"email": email, "password": "WrongPass@1"})
        return res.status_code == 401

    def test_login_nonexistent(self):
        res = self.client.post('/api/auth/login', json={
            "email": "nonexistent@test.edu", "password": "Test@1234"
        })
        return res.status_code == 401

    def test_login_empty(self):
        res = self.client.post('/api/auth/login', json={})
        return res.status_code == 400

    def test_profile_with_token(self):
        if not self.access_token_student:
            return False
        res = self.client.get('/api/auth/profile', headers={
            'Authorization': f'Bearer {self.access_token_student}'
        })
        data = res.get_json()
        return data['status'] == 'success' and 'user' in data

    def test_profile_without_token(self):
        res = self.client.get('/api/auth/profile')
        return res.status_code == 401

    def test_profile_invalid_token(self):
        res = self.client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer invalid.token.here'
        })
        return res.status_code == 401

    def test_profile_bad_token(self):
        res = self.client.get('/api/auth/profile', headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.invalid'
        })
        return res.status_code == 401

    def test_student_dashboard_access(self):
        if not self.access_token_student:
            return False
        res = self.client.get('/api/auth/student/dashboard-data', headers={
            'Authorization': f'Bearer {self.access_token_student}'
        })
        return res.status_code == 200

    def test_student_blocked_from_faculty(self):
        if not self.access_token_student:
            return False
        res = self.client.get('/api/auth/faculty/dashboard-data', headers={
            'Authorization': f'Bearer {self.access_token_student}'
        })
        return res.status_code == 403

    def test_faculty_dashboard_access(self):
        if not self.access_token_faculty:
            return False
        res = self.client.get('/api/auth/faculty/dashboard-data', headers={
            'Authorization': f'Bearer {self.access_token_faculty}'
        })
        return res.status_code == 200

    def test_faculty_user_list(self):
        if not self.access_token_faculty:
            return False
        res = self.client.get('/api/auth/users', headers={
            'Authorization': f'Bearer {self.access_token_faculty}'
        })
        data = res.get_json()
        return res.status_code == 200 and 'users' in data

    def test_token_refresh(self):
        if not self.refresh_token_student:
            return False
        res = self.client.post('/api/auth/refresh', json={
            "refresh_token": self.refresh_token_student
        })
        data = res.get_json()
        if data['status'] == 'success':
            self.access_token_student = data['access_token']
            return True
        return False

    def test_invalid_refresh(self):
        res = self.client.post('/api/auth/refresh', json={
            "refresh_token": "invalid-refresh-token"
        })
        return res.status_code == 401

    def test_forgot_password(self):
        res = self.client.post('/api/auth/forgot-password', json={
            "email": "login_test_s@test.edu"
        })
        data = res.get_json()
        return data['status'] == 'success'

    def test_reset_invalid_token(self):
        res = self.client.post('/api/auth/reset-password', json={
            "token": "invalid-token",
            "new_password": "NewPass@1234"
        })
        return res.status_code == 400

    def test_logout(self):
        if not self.access_token_student:
            return False
        res = self.client.post('/api/auth/logout',
            headers={'Authorization': f'Bearer {self.access_token_student}'},
            json={"refresh_token": self.refresh_token_student}
        )
        data = res.get_json()
        return data['status'] == 'success'

    def test_activity_log(self):
        if not self.access_token_faculty:
            return False
        res = self.client.get('/api/auth/activity', headers={
            'Authorization': f'Bearer {self.access_token_faculty}'
        })
        data = res.get_json()
        return data['status'] == 'success' and len(data['activities']) > 0

    def test_sql_injection(self):
        res = self.client.post('/api/auth/login', json={
            "email": "' OR 1=1 --",
            "password": "anything"
        })
        data = res.get_json()
        return data['status'] == 'error'

    def test_xss_sanitization(self):
        ts = str(int(time.time()))
        res = self.client.post('/api/auth/register', json={
            "name": "<script>alert('xss')</script>",
            "email": f"xss_{ts}@test.edu",
            "password": "Test@1234",
            "role": "student"
        })
        data = res.get_json()
        # Either the name is rejected by validation (400) — best case,
        # or if it gets through, the <script> tag must be sanitized
        if res.status_code == 400:
            return True  # Blocked by input validation — secure
        if data['status'] == 'success':
            return '<script>' not in data['user']['name']
        return False


if __name__ == '__main__':
    runner = AuthTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
