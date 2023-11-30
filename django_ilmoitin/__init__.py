import sys

import django

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata


__version__ = metadata.version("django_ilmoitin")


if django.VERSION < (3, 2):
    default_app_config = "django_ilmoitin.apps.DjangoIlmoitinConfig"
