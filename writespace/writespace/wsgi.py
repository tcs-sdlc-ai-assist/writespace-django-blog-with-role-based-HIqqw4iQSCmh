"""
WSGI config for writespace project.

It exposes the WSGI callable as a module-level variable named ``application``.
Also exposes ``app`` as an alias for Vercel's WSGI handler.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add the writespace project directory to sys.path so Django can find the apps
# This is necessary for Vercel serverless deployment where the working directory
# may not be the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writespace.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()

# Vercel expects the WSGI callable to be named 'app'
app = application