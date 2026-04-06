#!/bin/bash
# Build script for Vercel deployment
# Installs dependencies, collects static files, runs migrations, and creates default admin

set -e

echo "=== Installing requirements ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Creating default admin user ==="
python manage.py create_default_admin