"""
URL patterns for the users app.

These are included by config/urls.py under the prefix /api/auth/.
Final paths therefore are:
  /api/auth/login
  /api/auth/refresh
  /api/auth/me
"""

from django.urls import path

from .views import LoginView, MeView, TokenRefreshView

# app_name enables namespace-qualified reverse() lookups, e.g.:
#   reverse("users:login")
# This avoids name collisions if another app defines a 'login' URL.
app_name = "users"

urlpatterns = [
    # POST — exchange credentials for tokens
    path("login", LoginView.as_view(), name="login"),

    # POST — exchange a refresh token for a new access token
    path("refresh", TokenRefreshView.as_view(), name="token_refresh"),

    # GET — return the current user's profile
    path("me", MeView.as_view(), name="me"),
]
