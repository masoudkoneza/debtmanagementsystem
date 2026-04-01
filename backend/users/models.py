"""
Custom User model for the DMS.

Why a custom model?
  Django's built-in User model uses 'username' as the login identifier.
  The DMS spec requires 'email' as the primary login field, so we replace
  the default model entirely.  This must be done BEFORE any migrations —
  swapping AUTH_USER_MODEL after migrations exist requires a database reset.

Design decisions:
  - Inherits from AbstractBaseUser (password hashing, last_login) and
    PermissionsMixin (groups, permissions, is_superuser — needed for admin).
  - USERNAME_FIELD = "email" so authenticate(email=…, password=…) works.
  - REQUIRED_FIELDS contains fields prompted by createsuperuser (excludes
    USERNAME_FIELD and password, which are always asked).
  - tenant_id is nullable for now; it will be used in a future sprint when
    multi-tenancy is introduced.
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager required when USERNAME_FIELD != 'username'.

    Provides create_user() and create_superuser() helpers used by:
      - The Django management command 'createsuperuser'
      - Tests that bootstrap user fixtures
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user.

        Args:
            email:        Login identifier — normalised to lowercase.
            password:     Plain-text password; hashed before saving.
            extra_fields: Any other User field values (first_name, role, etc.).
        """
        if not email:
            raise ValueError("An email address is required.")

        # Normalise email: lower-case the domain part.
        email = self.normalize_email(email)

        # Set sensible defaults so callers don't have to repeat them.
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)   # Hashes the password using PBKDF2.
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser with Django admin access.

        Forces is_staff=True, is_superuser=True, and role=ADMIN so the
        superuser can reach every admin screen.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    DMS User model.

    Fields (spec §1.1):
      email       — Unique login identifier.
      first_name  — Required; max 100 characters.
      last_name   — Required; max 100 characters.
      role        — ADMIN or STAFF; defaults to STAFF.
      tenant_id   — UUID for future multi-tenancy; nullable for now.
      is_active   — False prevents login (403 on the auth endpoint).
      is_staff    — Grants access to the Django /admin/ interface.
      date_joined — Automatically set when the record is created.
    """

    class Role(models.TextChoices):
        """
        Enumerated role values.

        Using TextChoices keeps the DB values human-readable ('ADMIN', 'STAFF')
        so they can be used directly in JWT payloads and API responses without
        an extra mapping step.
        """
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"

    # -----------------------------------------------------------------------
    # Fields
    # -----------------------------------------------------------------------
    email = models.EmailField(
        unique=True,
        help_text="Primary login identifier. Must be unique across all users.",
    )
    first_name = models.CharField(
        max_length=100,
        help_text="User's given name. Required.",
    )
    last_name = models.CharField(
        max_length=100,
        help_text="User's family name. Required.",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
        help_text="Determines what the user can do in the DMS.",
    )
    tenant_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Reserved for multi-tenancy. Leave null until that sprint.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Inactive users cannot log in (API returns 403). "
            "Prefer deactivating over deleting to preserve audit trails."
        ),
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Grants access to the Django /admin/ interface.",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp set automatically when the record is first saved.",
    )

    # -----------------------------------------------------------------------
    # Manager & authentication configuration
    # -----------------------------------------------------------------------
    objects = UserManager()

    # Tell Django to use 'email' instead of 'username' for authentication.
    USERNAME_FIELD = "email"

    # Fields prompted by 'python manage.py createsuperuser' in addition to
    # USERNAME_FIELD (email) and password.
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    # -----------------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------------
    def get_full_name(self):
        """Return 'First Last', stripped of extra whitespace."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return just the first name (used by Django admin header)."""
        return self.first_name
