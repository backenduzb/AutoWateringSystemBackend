#!/bin/bash

set -e

# Django settings modulini set qilish
export DJANGO_SETTINGS_MODULE=core.settings.prod

echo "📦 Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "👤 Creating admin user (if not exists)..."
python manage.py createadmin

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn core.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -