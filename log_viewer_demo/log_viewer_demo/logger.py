import datetime

# All logging handlers configurations.
# 'propagate': False = mean is the error logs ins't duplicates to another file logs.

NOW = datetime.datetime.now()
DAY_NAME = NOW.strftime("%A").lower()

MAXIMUM_FILE_LOGS = 1024 * 1024 * 10  # 10 MB
BACKUP_COUNT = 5


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "[%(levelname)s] %(asctime)s %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/default.log",
            "maxBytes": MAXIMUM_FILE_LOGS,
            "backupCount": BACKUP_COUNT,
            "formatter": "standard",
        },
        "request_debug_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/request_debug.log",
            "maxBytes": MAXIMUM_FILE_LOGS,
            "backupCount": BACKUP_COUNT,
            "formatter": "standard",
        },
        "request_error_handler": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/request_error.log",
            "maxBytes": MAXIMUM_FILE_LOGS,
            "backupCount": BACKUP_COUNT,
            "formatter": "standard",
        },
        "mail_admins_handler": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "email_backend": "django.core.mail.backends.smtp.EmailBackend",
        },
    },
    "root": {"handlers": ["default"], "level": "DEBUG"},
    "loggers": {
        "django.request": {
            "handlers": [
                "request_debug_handler",
                "request_error_handler",
                "mail_admins_handler",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
