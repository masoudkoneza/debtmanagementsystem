"""
Tests for the DMS authentication endpoints.

All nine cases from the spec (§1.5) are covered here.
Run with:  python manage.py test users

Conventions used in this file:
  - setUp() creates one active STAFF user and one inactive user so every
    test can focus on the single behaviour it exercises.
  - Helper methods (_login, _get_me) reduce boilerplate and keep the
    intent of each test body clear.
  - Each test has a docstring explaining WHAT is being tested and WHY
    the expected status code is correct.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from .models import User


class AuthEndpointTests(TestCase):
    """
    Integration tests for /api/auth/login, /api/auth/refresh, /api/auth/me.

    Uses DRF's APIClient so that Authorization headers and JSON parsing
    are handled the same way as real HTTP requests.
    """

    # -----------------------------------------------------------------------
    # Fixtures
    # -----------------------------------------------------------------------

    def setUp(self):
        """
        Create the two users needed across most tests:
          self.active_user   — normal STAFF user who can log in.
          self.inactive_user — account disabled (is_active=False).

        Both users have known passwords so tests can assert on login behaviour.
        """
        self.client = APIClient()

        self.active_password = "StrongPass123!"
        self.active_user = User.objects.create_user(
            email="active@example.com",
            password=self.active_password,
            first_name="Active",
            last_name="User",
            role=User.Role.STAFF,
            is_active=True,
        )

        self.inactive_password = "StrongPass123!"
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password=self.inactive_password,
            first_name="Inactive",
            last_name="User",
            role=User.Role.STAFF,
            is_active=False,  # This user cannot log in.
        )

    # -----------------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------------

    def _login(self, email, password):
        """POST to /api/auth/login and return the response."""
        return self.client.post(
            "/api/auth/login",
            {"email": email, "password": password},
            format="json",
        )

    def _get_me(self, token):
        """
        GET /api/auth/me with a Bearer token.

        Sets the Authorization header on the client for this call only.
        After the call the header is cleared so other tests start clean.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/me")
        self.client.credentials()  # Clear credentials after the request.
        return response

    def _refresh(self, refresh_token):
        """POST to /api/auth/refresh and return the response."""
        return self.client.post(
            "/api/auth/refresh",
            {"refresh": refresh_token},
            format="json",
        )

    # -----------------------------------------------------------------------
    # Test cases (spec §1.5)
    # -----------------------------------------------------------------------

    def test_login_valid_credentials_returns_200_with_tokens(self):
        """
        Spec: "Login with valid credentials returns 200 and both tokens."

        On a successful login the response must contain:
          - access_token
          - refresh_token
          - user object with id, email, first_name, last_name, role
        """
        response = self._login(self.active_user.email, self.active_password)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertIn("user", data)

        user = data["user"]
        self.assertEqual(user["email"], self.active_user.email)
        self.assertEqual(user["first_name"], self.active_user.first_name)
        self.assertEqual(user["last_name"], self.active_user.last_name)
        self.assertEqual(user["role"], self.active_user.role)

    def test_login_wrong_password_returns_401(self):
        """
        Spec: "Login with wrong password returns 401."

        Security requirement: the error message must NOT reveal whether the
        email exists.  We assert on the status code only, not the message text.
        """
        response = self._login(self.active_user.email, "WrongPassword!")
        self.assertEqual(response.status_code, 401)

    def test_login_unknown_email_returns_401(self):
        """
        Spec: "Login with unknown email returns 401."

        Same vague message as wrong password — prevents email enumeration
        (an attacker should not be able to confirm that an email is registered).
        """
        response = self._login("nobody@example.com", "AnyPassword!")
        self.assertEqual(response.status_code, 401)

    def test_login_missing_email_returns_400(self):
        """
        Spec: "Login with missing email or password returns 400."

        Missing required fields should return 400 with field-level errors,
        not 401 — the request is malformed, not an auth failure.
        """
        response = self.client.post(
            "/api/auth/login",
            {"password": self.active_password},  # email omitted
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        # DRF serialiser error keys match field names.
        self.assertIn("email", response.json())

    def test_login_missing_password_returns_400(self):
        """
        Spec: "Login with missing email or password returns 400."

        Password is a required field.  Omitting it is a client error (400),
        not an authentication failure (401).
        """
        response = self.client.post(
            "/api/auth/login",
            {"email": self.active_user.email},  # password omitted
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())

    def test_login_inactive_user_returns_403(self):
        """
        Spec: "Login as inactive user returns 403."

        A 403 (Forbidden) is distinct from 401 (Unauthorised) — it signals
        that the credentials are correct but the account has been disabled.
        The frontend can show a more specific message ("contact your admin").
        """
        response = self._login(self.inactive_user.email, self.inactive_password)
        self.assertEqual(response.status_code, 403)

    def test_get_me_with_valid_token_returns_correct_user_data(self):
        """
        Spec: "GET /api/auth/me with valid token returns correct user data."

        The response must include all fields defined in spec §1.2 /me:
          id, email, first_name, last_name, role, tenant_id, date_joined.
        """
        # First log in to get a valid access token.
        login_response = self._login(self.active_user.email, self.active_password)
        access_token = login_response.json()["access_token"]

        response = self._get_me(access_token)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Assert every field the spec requires is present and correct.
        self.assertEqual(data["email"], self.active_user.email)
        self.assertEqual(data["first_name"], self.active_user.first_name)
        self.assertEqual(data["last_name"], self.active_user.last_name)
        self.assertEqual(data["role"], self.active_user.role)
        self.assertIn("id", data)
        self.assertIn("tenant_id", data)   # null is fine
        self.assertIn("date_joined", data)

    def test_get_me_with_no_token_returns_401(self):
        """
        Spec: "GET /api/auth/me with no token returns 401."

        Without an Authorization header the JWTAuthentication backend
        rejects the request before it reaches the view.
        """
        # Deliberately do NOT set any credentials.
        response = self.client.get("/api/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_refresh_with_valid_token_returns_new_access_token(self):
        """
        Spec: "POST /api/auth/refresh with valid token returns new access token."

        The refresh endpoint should return a new access_token string.
        We do a basic sanity check that the token is non-empty; full JWT
        validation is covered by simplejwt's own test suite.
        """
        # Log in to get a refresh token.
        login_response = self._login(self.active_user.email, self.active_password)
        refresh_token = login_response.json()["refresh_token"]

        response = self._refresh(refresh_token)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertTrue(len(data["access_token"]) > 0)

    def test_refresh_with_invalid_token_returns_401(self):
        """
        Spec: "POST /api/auth/refresh with invalid token returns 401."

        A made-up string is not a valid JWT and should be rejected.
        """
        response = self._refresh("this.is.not.a.real.token")
        self.assertEqual(response.status_code, 401)
