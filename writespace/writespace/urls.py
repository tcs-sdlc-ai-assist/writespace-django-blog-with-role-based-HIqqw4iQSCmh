"""
URL configuration for writespace project.

Root URL dispatcher that wires all app URL patterns together.
Includes blog URLs at the root level, account URLs under /accounts/,
and Django admin site URLs under /admin/.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("blog.urls")),
]