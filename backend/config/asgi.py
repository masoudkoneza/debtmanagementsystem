"""
ASGI config for the DMS project.

Exposes the ASGI callable as module-level 'application'.
Required for async-capable servers (e.g. Daphne, Uvicorn).
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
