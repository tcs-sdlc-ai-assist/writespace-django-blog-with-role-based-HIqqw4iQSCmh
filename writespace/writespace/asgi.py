"""
ASGI config for writespace project.

It exposes the ASGI callable as a module-level variable named ``application``.
Also exposes ``app`` as an alias for compatibility with ASGI servers.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

# Add the writespace project directory to sys.path so Django can find the apps
# This is necessary for deployment environments where the working directory
# may not be the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writespace.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

application = get_asgi_application()

# Alias for ASGI servers that expect the callable to be named 'app'
app = application