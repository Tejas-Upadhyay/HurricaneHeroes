#!/bin/bash
# Startup script for Azure App Service (Linux Web App)
# This script runs database migrations, collects static files, and starts Gunicorn.

set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Running Azure App Service Startup Tasks..."

# Run database migrations
echo "⚙️ Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "⚡ Starting Gunicorn..."
gunicorn --bind=0.0.0.0 --timeout 600 relief_system.wsgi:application
