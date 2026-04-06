"""Management command to create a default admin user for deployment."""

import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create a default admin superuser if one does not already exist.

    Reads credentials from environment variables with sensible defaults.
    Intended to be run during deployment (e.g., in build_files.sh).
    """

    help = "Creates a default admin superuser if it does not already exist."

    def handle(self, *args, **options):
        """Execute the command to create the default admin user."""
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Default admin user "{username}" already exists. Skipping.'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Default admin user "{username}" created successfully.'
            )
        )