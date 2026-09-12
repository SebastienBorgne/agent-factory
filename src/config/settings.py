from pathlib import Path

from .env import load_settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

APP_SETTINGS = load_settings(BASE_DIR)

SECRET_KEY = APP_SETTINGS.django.secret_key
DEBUG = APP_SETTINGS.django.debug
ALLOWED_HOSTS = APP_SETTINGS.django.allowed_hosts

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "infrastructure.django_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "infrastructure" / "web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

TEST_RUNNER = "config.test_runner.ProjectTestRunner"

if APP_SETTINGS.database.host:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": APP_SETTINGS.database.name,
            "USER": APP_SETTINGS.database.user,
            "PASSWORD": APP_SETTINGS.database.password,
            "HOST": APP_SETTINGS.database.host,
            "PORT": APP_SETTINGS.database.port,
        }
    }
else:
    # No Postgres host configured (e.g. running tests/dev without docker
    # compose up) -- fall back to a local sqlite file.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- agent-factory specific settings ---
AGENT_TEMPLATES_ROOT = str(BASE_DIR / "agent_templates")
GENERATED_TEAMS_ROOT = APP_SETTINGS.paths.generated_teams_root
KAFKA_BOOTSTRAP_SERVERS = APP_SETTINGS.kafka.bootstrap_servers
