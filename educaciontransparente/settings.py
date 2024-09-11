import logging
import sys
from os import getenv
from pathlib import Path

from django.urls import reverse_lazy
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")

SECRET_KEY = getenv("SECRET_KEY")

ENVIRONMENT = getenv("ENVIRONMENT").lower()

DEBUG = (
    getenv("DEBUG").lower() in ("true", "1")
    if ENVIRONMENT in ("local", "development")
    else False
)

if DEBUG:
    logging.warning("DEBUG MODE ON")

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_filters",
    "rest_framework",
    "accountability.apps.AccountabilityConfig",
    "core.apps.CoreConfig",
    "users.apps.UsersConfig",
    "website.apps.WebsiteConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangorestframework_camel_case.middleware.CamelCaseMiddleWare",
]

ROOT_URLCONF = "educaciontransparente.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "educaciontransparente/templates"],
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

WSGI_APPLICATION = "educaciontransparente.wsgi.application"

DEFAULT_DATABASE = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": getenv("DB_NAME"),
    "USER": getenv("DB_USER"),
    "PASSWORD": getenv("DB_PASSWORD"),
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
}

TEST_DATABASE = {
    "ENGINE": "django.db.backends.sqlite3",
    "TEST_CHARSET": "UTF8",
    "NAME": "file:default?mode=memory",
    "OPTIONS": {
        "timeout": 30,
    },
}

IS_TEST = "pytest" in sys.argv[0]

DATABASES = {"default": TEST_DATABASE if IS_TEST else DEFAULT_DATABASE}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Asuncion"

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / "static"

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static_src",
]

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "console_debug": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": getenv("LOG_LEVEL", "INFO"),
        },
    },
}

UNFOLD = {
    "SITE_TITLE": "Educación Transparente",
    "SHOW_VIEW_ON_SITE": False,
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Principal",
                "items": [
                    {
                        "title": "Resoluciones",
                        "icon": "history_edu",
                        "link": reverse_lazy(
                            "admin:accountability_resolution_changelist"
                        ),
                    },
                    {
                        "title": "Desembolsos",
                        "icon": "paid",
                        "link": reverse_lazy(
                            "admin:accountability_disbursement_changelist"
                        ),
                    },
                    {
                        "title": "Rendiciones",
                        "icon": "quick_reference_all",
                        "link": reverse_lazy("admin:accountability_report_changelist"),
                    },
                    {
                        "title": "Comprobantes",
                        "icon": "receipt",
                        "link": reverse_lazy("admin:accountability_receipt_changelist"),
                    },
                    {
                        "title": "Proveedores",
                        "icon": "receipt",
                        "link": reverse_lazy(
                            "admin:accountability_provider_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "Configuraciones",
                "items": [
                    {
                        "title": "Instituciones",
                        "icon": "corporate_fare",
                        "link": reverse_lazy("admin:core_institution_changelist"),
                    },
                    {
                        "title": "Usuarios",
                        "icon": "person",
                        "link": reverse_lazy("admin:users_user_changelist"),
                    },
                    {
                        "title": "Origen del ingreso",
                        "icon": "payment",
                        "link": reverse_lazy(
                            "admin:accountability_disbursementorigin_changelist"
                        ),
                    },
                    {
                        "title": "Marcos",
                        "icon": "book",
                        "link": reverse_lazy(
                            "admin:accountability_origindetail_changelist"
                        ),
                    },
                ],
            },
            {
                "title": "Administración",
                "items": [
                    {
                        "title": "Recursos",
                        "icon": "article",
                        "link": reverse_lazy("admin:core_resource_changelist"),
                    },
                    {
                        "title": "Departamentos",
                        "icon": "map",
                        "link": reverse_lazy("admin:core_department_changelist"),
                    },
                    {
                        "title": "Distritos",
                        "icon": "location_city",
                        "link": reverse_lazy("admin:core_district_changelist"),
                    },
                    {
                        "title": "Localidades",
                        "icon": "streetview",
                        "link": reverse_lazy("admin:core_locality_changelist"),
                    },
                    {
                        "title": "Establecimientos",
                        "icon": "location_on",
                        "link": reverse_lazy("admin:core_establishment_changelist"),
                    },
                    {
                        "title": "Objetos de gasto",
                        "icon": "category",
                        "link": reverse_lazy(
                            "admin:accountability_accountobject_changelist"
                        ),
                    },
                    {
                        "title": "Tipos de pago",
                        "icon": "attach_money",
                        "link": reverse_lazy(
                            "admin:accountability_paymenttype_changelist"
                        ),
                    },
                    {
                        "title": "Tipos de comprobante",
                        "icon": "file_present",
                        "link": reverse_lazy(
                            "admin:accountability_receipttype_changelist"
                        ),
                    },
                ],
            },
        ]
    },
}

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/min",
    },
    "DEFAULT_PAGINATION_CLASS": "core.pagination.SitePagination",
}

JSON_CAMEL_CASE = {"RENDERER_CLASS": "drf_orjson_renderer.renderers.ORJSONRenderer"}

USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = "."

EMAIL_BACKEND = (
    "django.core.mail.backends.console.EmailBackend"
    if getenv("TEST_EMAIL").lower() in ("true", "1")
    else "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_USE_TLS = True
EMAIL_PORT = getenv("EMAIL_PORT")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_FROM = getenv("EMAIL_FROM", EMAIL_HOST_USER)
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
