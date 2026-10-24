"""Gunicorn settings, auto-loaded from the working directory. Override via env vars."""

import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
accesslog = "-"
# The runtime user has no writable home; the control socket isn't needed in containers.
control_socket_disable = True
