#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

Usage:
  python manage.py runserver          # Start the dev server
  python manage.py makemigrations     # Generate migration files
  python manage.py migrate            # Apply migrations
  python manage.py test users         # Run the auth test suite
  python manage.py createsuperuser    # Create an admin user
"""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and that you "
            "activated your virtual environment."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
