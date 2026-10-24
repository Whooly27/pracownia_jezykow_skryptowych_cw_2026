"""WSGI entrypoint, used by gunicorn in the container image and by Vercel."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()

# Vercel's Python runtime looks for a module-level `app`.
app = application
