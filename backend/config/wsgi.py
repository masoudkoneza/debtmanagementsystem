"""
WSGI config for the DMS project.

Exposes the WSGI callable as module-level 'application'.
Used by Gunicorn (production) or Django's built-in dev server.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
