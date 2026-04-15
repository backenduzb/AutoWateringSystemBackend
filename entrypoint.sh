#!/bin/bash

set -e

export DJANGO_SETTINGS_MODULE=core.settings

echo "📦 Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

python manage.py createadmin

exec gunicorn core.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -