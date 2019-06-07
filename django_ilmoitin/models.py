import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .registry import notifications

logger = logging.getLogger(__name__)


class NotificationTemplateException(Exception):
    pass


class NotificationTemplate(TranslatableModel):
    _type = models.CharField(
        max_length=50,
        verbose_name=_("type"),
        unique=True,
        db_column="type",
        choices=list(notifications.registry.items()),
    )

    translations = TranslatedFields(
        subject=models.CharField(verbose_name=_("subject"), max_length=255),
        body_html=models.TextField(verbose_name=_("body, HTML version"), blank=True),
        body_text=models.TextField(
            verbose_name=_("body, plain text version"),
            blank=True,
            help_text=_(
                "If left blank, the HTML version without HTML tags will be used."
            ),
        ),
    )

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self):
        return str(self.type)

    @property
    def type(self):
        return notifications.registry.get(self._type)

    @type.setter
    def type(self, value):
        self._type = value
