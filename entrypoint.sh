#!/bin/sh

set -e

python manage.py makemigrations --no-input
python manage.py migrate --no-input

python manage.py createadmin

# WSGI (gunicorn) cannot serve WebSockets. Use ASGI so ESP32 + browser can connect.
daphne -b 0.0.0.0 -p 8000 core.asgi:application
