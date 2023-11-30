from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoIlmoitinConfig(AppConfig):
    name = "django_ilmoitin"
    verbose_name = _("Ilmoitin")
    default_auto_field = 'django.db.models.BigAutoField'
