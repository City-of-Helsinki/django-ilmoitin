from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoIlmoitinConfig(AppConfig):
    name = "django_ilmoitin"
    verbose_name = _("Ilmoitin")
