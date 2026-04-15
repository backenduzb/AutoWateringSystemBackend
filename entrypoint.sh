#!/bin/sh

set -e

python manage.py makemigrations --no-input
python manage.py migrate --no-input

python manage.py createadmin

gunicorn core.asgi:application -k uvicorn.workers.UvicornWorker