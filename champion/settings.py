"""
==============================================================
  LE CHAMPION SUPERMARCHÉ TOGO — settings.py
  Configuration Django complète
  - PostgreSQL
  - Fichiers statiques & médias
  - Sécurité production
  - Email SMTP
  - Cache
  - Logging
  - Internationalisation (fr-fr / Africa/Lome)
==============================================================
"""

import os
from pathlib import Path
import environ



environ.Env.read_env(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# ── Racine du projet ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Lecture du fichier .env ──────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    DB_PORT=(int, 5432),
    DB_CONN_MAX_AGE=(int, 60),
    SECURE_SSL_REDIRECT=(bool, False),
    SECURE_HSTS_SECONDS=(int, 0),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    LOG_LEVEL=(str, "INFO"),
)

ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f"Fichier .env introuvable : {ENV_FILE}\n"
        f"BASE_DIR détecté : {BASE_DIR}\n"
        "Copiez .env.example en .env à la racine du projet."
    )

environ.Env.read_env(ENV_FILE)

# Cherche le .env à la racine du projet
environ.Env.read_env(BASE_DIR / ".env")
#MAPBOX_ACCESS_TOKEN = env("MAPBOX_ACCESS_TOKEN")  # via django-environ ou os.environ

# ==============================================================
# CORE
# ==============================================================

SECRET_KEY = env("SECRET_KEY")
DEBUG       = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


MAPBOX_ACCESS_TOKEN = env("MAPBOX_ACCESS_TOKEN")  

# Application de confiance pour les proxies inverses (nginx)
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if not h.startswith(("localhost", "127"))
]

MAGASIN_WHATSAPP = "22893040702" 
# ==============================================================
# APPLICATIONS
# ==============================================================

# ✅ DJANGO_APPS — uniquement les apps Django natives
DJANGO_APPS = [
    "import_export",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "django_cleanup",
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "fr"
MODELTRANSLATION_LANGUAGES = ("fr", "en")

# ✅ LOCAL_APPS — uniquement tes applications
LOCAL_APPS = [
    "supermarche.apps.SupermarheConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ==============================================================
# MIDDLEWARE
# ==============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # statiques en prod sans nginx
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",      # i18n
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==============================================================
# URLs & WSGI
# ==============================================================

ROOT_URLCONF = "champion.urls"
WSGI_APPLICATION = "champion.wsgi.application"


# ==============================================================
# TEMPLATES
# ==============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # templates globaux du projet
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",    # {{ MEDIA_URL }}
                "django.template.context_processors.static",   # {{ STATIC_URL }}
                "django.template.context_processors.i18n",
                "supermarche.context_processors.panier_context",  # ← ajout
                "supermarche.context_processors.nav_active_context",  # ← ajout
            ],
        },
    },
]


# ==============================================================
# BASE DE DONNÉES — PostgreSQL
# ==============================================================

DATABASES = {
    "default": {
        "ENGINE":       env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME":         env("DB_NAME"),
        "USER":         env("DB_USER"),
        "PASSWORD":     env("DB_PASSWORD"),
        "HOST":         env("DB_HOST", default="localhost"),
        "PORT":         env("DB_PORT"),
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),
        "OPTIONS": {
            # Encodage UTF-8 forcé côté client PostgreSQL
            "client_encoding": "UTF8",
            # Timeout de connexion (secondes)
            "connect_timeout": 10,
        },
        "TEST": {
            "NAME": f"test_{env('DB_NAME')}",
        },
    }
}

# Auto-field par défaut pour les clés primaires
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================================================
# FICHIERS STATIQUES
# ==============================================================

# URL publique pour les assets statiques
STATIC_URL = env("STATIC_URL", default="/static/")

# Répertoire de sortie de `collectstatic` (production)
STATIC_ROOT = env("STATIC_ROOT", default=str(BASE_DIR / "staticfiles"))

# Répertoires supplémentaires où Django cherche des statiques
STATICFILES_DIRS = [
    BASE_DIR / "static",   # static/ à la racine du projet
]

# Finders (ordre de résolution)
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# WhiteNoise : compression & cache immutable en production
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
    if not DEBUG
    else "django.contrib.staticfiles.storage.StaticFilesStorage"
)


# ==============================================================
# FICHIERS MÉDIAS (uploads)
# ==============================================================

# URL publique pour les fichiers uploadés
MEDIA_URL = env("MEDIA_URL", default="/media/")

# Répertoire physique de stockage des uploads
MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "media"))


# ==============================================================
# CACHE
# ==============================================================

CACHES = {
    "default": {
        "BACKEND":  env("CACHE_BACKEND",
                        default="django.core.cache.backends.locmem.LocMemCache"),
        "LOCATION": env("CACHE_LOCATION", default="lechampion-cache"),
        "TIMEOUT":  300,   # 5 minutes par défaut
        "OPTIONS": {
            "MAX_ENTRIES": 2000,
        },
    }
}

# Cache des sessions
SESSION_ENGINE      = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE  = 86400 * 14   # 14 jours
SESSION_COOKIE_NAME = "lechampion_session"


# ==============================================================
# VALIDATION DES MOTS DE PASSE
# ==============================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ==============================================================
# INTERNATIONALISATION
# ==============================================================

LANGUAGE_CODE = env("LANGUAGE_CODE", default="fr-fr")
TIME_ZONE     = env("TIME_ZONE",      default="Africa/Lome")
USE_I18N      = True
USE_L10N      = True
USE_TZ        = True


# ==============================================================
# EMAIL
# ==============================================================

EMAIL_BACKEND       = env("EMAIL_BACKEND",
                          default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST          = env("EMAIL_HOST",          default="localhost")
EMAIL_PORT          = env.int("EMAIL_PORT",       default=25)
EMAIL_USE_TLS       = env.bool("EMAIL_USE_TLS",   default=False)
EMAIL_HOST_USER     = env("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = env("DEFAULT_FROM_EMAIL",  default="noreply@lechampion.tg")
SERVER_EMAIL        = env("SERVER_EMAIL",         default="errors@lechampion.tg")

# Administrateurs notifiés par email en cas d'erreur 500
ADMINS = [
    ("Admin Le Champion", env("ADMIN_EMAIL", default="admin@lechampion.tg")),
]


# ==============================================================
# SÉCURITÉ (valeurs durcies en production)
# ==============================================================

# HTTPS
SECURE_SSL_REDIRECT       = env("SECURE_SSL_REDIRECT")
SECURE_HSTS_SECONDS       = env("SECURE_HSTS_SECONDS")
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD            = SECURE_HSTS_SECONDS > 0
SECURE_BROWSER_XSS_FILTER     = True
SECURE_CONTENT_TYPE_NOSNIFF    = True

# Cookies sécurisés
SESSION_COOKIE_SECURE     = env("SESSION_COOKIE_SECURE")
SESSION_COOKIE_HTTPONLY   = True
SESSION_COOKIE_SAMESITE   = "Lax"
CSRF_COOKIE_SECURE        = env("CSRF_COOKIE_SECURE")
CSRF_COOKIE_HTTPONLY      = True

# Clickjacking
X_FRAME_OPTIONS = "SAMEORIGIN"   # autorise les iframes du même domaine (Google Maps)


# ==============================================================
# LOGGING
# ==============================================================

LOG_DIR   = Path(env("LOG_DIR", default=str(BASE_DIR / "logs")))
LOG_LEVEL = env("LOG_LEVEL")

# Créer le répertoire de logs s'il n'existe pas
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # ── Formateurs ───────────────────────────────────────────
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} — {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {asctime} — {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "console": {
            "format": "[\033[1;{color}m{levelname}\033[0m] {asctime} {module} — {message}",
            "style": "{",
        },
    },

    # ── Filtres ──────────────────────────────────────────────
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },

    # ── Handlers ─────────────────────────────────────────────
    "handlers": {
        # Console (développement uniquement)
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        # Fichier d'application général (rotation journalière)
        "file_app": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "when": "midnight",
            "backupCount": 30,
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        # Fichier dédié aux erreurs
        "file_errors": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "when": "midnight",
            "backupCount": 60,
            "encoding": "utf-8",
            "formatter": "verbose",
        },
        # Fichier dédié aux requêtes SQL (DEBUG seulement)
        "file_db": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "db.log"),
            "maxBytes": 5 * 1024 * 1024,   # 5 Mo
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "simple",
        },
        # Email aux admins sur erreurs critiques (prod)
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },

    # ── Loggers ──────────────────────────────────────────────
    "loggers": {
        # Application principale
        "supermarche": {
            "handlers": ["console", "file_app", "file_errors"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # Requêtes Django
        "django": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        # Requêtes HTTP
        "django.request": {
            "handlers": ["file_errors", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        # Sécurité
        "django.security": {
            "handlers": ["file_errors", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        # Requêtes SQL (activé seulement en debug)
        "django.db.backends": {
            "handlers": ["file_db"],
            "level": "DEBUG",
            "propagate": False,
        },
    },

    # ── Root logger (fallback) ───────────────────────────────
    "root": {
        "handlers": ["console", "file_errors"],
        "level": "WARNING",
    },
}


# ==============================================================
# MESSAGES (flash)
# ==============================================================

from django.contrib.messages import constants as messages_constants

MESSAGE_TAGS = {
    messages_constants.DEBUG:   "debug",
    messages_constants.INFO:    "info",
    messages_constants.SUCCESS: "success",
    messages_constants.WARNING: "warning",
    messages_constants.ERROR:   "danger",
}


# ==============================================================
# UPLOAD — Limites et types autorisés
# ==============================================================

# Taille max d'un fichier uploadé : 10 Mo
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Répertoire temporaire pour les gros uploads
FILE_UPLOAD_TEMP_DIR = BASE_DIR / "media" / "tmp"
FILE_UPLOAD_TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================
# PAGINATION PAR DÉFAUT (utilisée dans les CBV)
# ==============================================================

PAGINATE_BY = 24


# ==============================================================
# CONFIGURATION SPÉCIFIQUE AU PROJET
# ==============================================================

# Nombre de produits en avant sur l'accueil
ACCUEIL_NB_NOUVEAUTES      = 8
ACCUEIL_NB_COUPS_DE_COEUR  = 8
ACCUEIL_NB_PROMO           = 8

# Nombre maximum de résultats de recherche par catégorie
RECHERCHE_MAX_PRODUITS  = 12
RECHERCHE_MAX_RECETTES  = 6
RECHERCHE_MAX_ARTICLES  = 6
RECHERCHE_MAX_PROMOS    = 4