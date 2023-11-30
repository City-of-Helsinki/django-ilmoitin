import django

from importlib import metadata


__version__ = metadata.version("django_ilmoitin")


if django.VERSION < (3, 2):
    default_app_config = "django_ilmoitin.apps.DjangoIlmoitinConfig"
