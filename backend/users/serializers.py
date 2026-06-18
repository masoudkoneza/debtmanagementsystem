"""
Serializers for the DMS authentication endpoints.

Serializers serve two purposes here:
  1. Validate incoming request data (LoginSerializer).
  2. Shape outgoing response data (UserSerializer, LoginResponseSerializer).

Keeping serializers separate from views makes them easier to unit-test
and re-use across different views or API versions.
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for the user object returned in responses.

    Used in:
      - POST /api/auth/login  (nested inside the login response)
      - GET  /api/auth/me     (full profile response)

    'tenant_id' is included in /me but omitted from the login response;
    that distinction is handled at the view level by passing 'fields' or
    by using separate serializer subclasses.
    """

    class Meta:
        model = User
        # Expose only the fields the frontend needs — never expose password
        # hashes, internal flags, or Django permission fields.
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "tenant_id",
            "date_joined",
        ]
        # All fields are read-only; this serializer is never used for writes.
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """
    Validates the body of POST /api/auth/login.

    Validation order:
      1. Both fields must be present (required=True, enforced by DRF).
      2. The email/password pair must match an active user.

    Security note: validate() raises a generic 'Invalid credentials' error
    whether the email is unknown OR the password is wrong.  Returning
    different messages for the two cases would allow email enumeration.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Registered email address.",
    )
    password = serializers.CharField(
        required=True,
        write_only=True,   # Never echo the password back in any response.
        style={"input_type": "password"},
        help_text="Account password.",
    )

    def validate(self, attrs):
        """
        Attempt to authenticate the supplied credentials.

        Django's authenticate() checks the password and returns None if:
          - The email does not exist, OR
          - The password is wrong.
        Both cases are mapped to the same error message (spec §1.2 / 401).

        If the user exists but is inactive, authenticate() still returns None,
        but we want a 403 in that case.  We therefore check explicitly.
        """
        email = attrs["email"]
        password = attrs["password"]

        # First, check whether the email exists at all so we can differentiate
        # 'wrong password / unknown email' (401) from 'inactive account' (403).
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            # Email not found — return the same vague error as wrong password.
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]},
                code="authentication_failed",
            )

        # Email exists but account is disabled.
        if not user_obj.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["account_inactive"]},
                code="account_inactive",
            )

        # Verify the password.
        user = authenticate(
            request=self.context.get("request"),
            username=email,    # Django's authenticate() uses USERNAME_FIELD
            password=password,
        )

        if user is None:
            # Password mismatch — same vague message as unknown email.
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials."]},
                code="authentication_failed",
            )

        # Stash the authenticated user on the serializer so the view can
        # access it without doing a second DB lookup.
        attrs["user"] = user
        return attrs
