import urllib.parse as up
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def _normalize_env_value(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().strip('"').strip("'")


def get_debug(key: str) -> bool:
    raw = getenv(key, "false")
    normalized = _normalize_env_value(raw).lower()
    return normalized in {"yes", "true", "1"}

def get_env_list(variable: str, sep: str = ",", default: list = []) -> list:
    variable = getenv(variable, "")
    variables = [i.strip() for i in variable.split(sep) if i.strip()]
    for host in variables:
        default.append(host)
    
    return default

def get_env_database(base_dir, database_url: str = "", debug: bool = True) -> dict:
    database_url = getenv(database_url, "")
    
    if debug:
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": base_dir / "db.sqlite3",
            }
        }

    if not database_url:
        raise ValueError("DATABASE_PUBLIC_URL not set for production!")

    url = up.urlparse(database_url)
    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path.lstrip("/"),
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname or "localhost",
            "PORT": url.port or 5432,
        }
    }
