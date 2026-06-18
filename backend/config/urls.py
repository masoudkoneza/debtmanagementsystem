"""
URL configuration for the DMS backend.

All authentication endpoints live under /api/auth/ (spec §1.2).
The Django admin is kept at /admin/ for superuser convenience.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Mount the users app's auth routes.
    # All endpoints become /api/auth/<endpoint>/ — see users/urls.py.
    path("api/auth/", include("users.urls")),
]
