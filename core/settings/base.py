from pathlib import Path
from common.utils.env import (
    get_env_database, get_debug, getenv
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = getenv("DJANGO_SECRET", "dev-insecure-change-me")

DEBUG = get_debug("DEBUG")

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'channels',
    'rest_framework',
    'django_filters',
    'corsheaders',
    
    'apps.auth.apps.AuthConfig',
    'apps.sensors.apps.SensorsConfig',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = get_env_database(
    base_dir=BASE_DIR,
    database_url="DATABASE_PUBLIC_URL",
    debug=DEBUG
)

ASGI_APPLICATION = "core.asgi.application"
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
}

TELEMETRY_DEVICE_TOKENS = [
    t.strip()
    for t in getenv(
        "TELEMETRY_DEVICE_TOKENS",
        getenv("ESP32_WS_SECRET", "esp32-secret"),
    ).split(",")
    if t.strip()
]

AUTH_USER_MODEL = "accounts.User"

MIGRATION_MODULES = {
    "accounts": "migrations2.accounts",
    "sensors": "migrations.sensors",
}
