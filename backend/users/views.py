"""
Views for the DMS authentication API.

Endpoints (spec §1.2):
  POST /api/auth/login    — Exchange credentials for JWT tokens.
  POST /api/auth/refresh  — Exchange a refresh token for a new access token.
  GET  /api/auth/me       — Return the profile of the currently logged-in user.

All views use Django REST Framework class-based views for consistency
and to make permission/authentication overrides explicit.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserSerializer


class LoginView(APIView):
    """
    POST /api/auth/login

    Accepts { email, password } and returns:
      200 — access_token, refresh_token, and a user object.
      400 — Field-level validation errors (missing email or password).
      401 — Invalid credentials (wrong email OR wrong password).
      403 — Account is inactive.

    This endpoint is deliberately public (AllowAny) because the user
    has not authenticated yet.
    """

    # Override the default IsAuthenticated permission — login must be public.
    permission_classes = [AllowAny]

    def post(self, request):
        # Pass the raw request data into the serializer for validation.
        # We forward 'request' in context so LoginSerializer can call
        # Django's authenticate() with the correct request object.
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            # Check whether the failure is a 403 (inactive) or 401/400.
            errors = serializer.errors

            # The LoginSerializer encodes inactive-account errors with the
            # special marker 'account_inactive' in non_field_errors.
            non_field = errors.get("non_field_errors", [])
            if any("account_inactive" in str(e) for e in non_field):
                return Response(
                    {"detail": "Account is inactive."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Distinguish 'Invalid credentials' (401) from missing fields (400).
            # If the only error key is non_field_errors, it's an auth failure.
            auth_error_codes = {"authentication_failed"}
            is_auth_error = all(
                getattr(e, "code", None) in auth_error_codes
                for e in non_field
            )

            if non_field and is_auth_error:
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Everything else is a 400 — e.g. missing required fields.
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Validation passed; the authenticated user is stashed on the serializer.
        user = serializer.validated_data["user"]

        # Generate a JWT refresh token for this user.
        # The access token is derived from the refresh token object.
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Serialise only the fields the login response should expose.
        # We exclude tenant_id and date_joined from the login response —
        # those are available on /api/auth/me.
        user_data = UserSerializer(user).data
        login_user = {
            "id": user_data["id"],
            "email": user_data["email"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "role": user_data["role"],
        }

        return Response(
            {
                "access_token": str(access),
                "refresh_token": str(refresh),
                "user": login_user,
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    """
    POST /api/auth/refresh

    Accepts { refresh } and returns:
      200 — { access_token: "<new JWT>" }
      401 — Invalid or expired refresh token.

    We wrap simplejwt's built-in TokenRefreshSerializer rather than
    re-implementing the rotation logic ourselves, so we stay in sync
    with library updates automatically.
    """

    # Token refresh is a public endpoint — the caller has no access token yet.
    permission_classes = [AllowAny]

    def post(self, request):
        # simplejwt expects the key to be named 'refresh'.
        serializer = TokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            # simplejwt raises TokenError for expired/invalid/blacklisted tokens.
            raise InvalidToken(e.args[0])

        # simplejwt returns { "access": "..." } — rename to match our API style.
        return Response(
            {"access_token": serializer.validated_data["access"]},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /api/auth/me

    Returns the full profile of the currently authenticated user.

    Requires a valid Bearer token in the Authorization header.
      200 — Full user profile (id, email, names, role, tenant_id, date_joined).
      401 — No token, expired token, or invalid token.

    IsAuthenticated is redundant here since it's the global default (set in
    settings.py), but it is stated explicitly for clarity during code review.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user is populated by JWTAuthentication middleware after
        # it validates the Bearer token in the Authorization header.
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
