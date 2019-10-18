import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .registry import notifications

logger = logging.getLogger(__name__)


def get_default_from_email():
    return settings.DEFAULT_FROM_EMAIL


class NotificationTemplateException(Exception):
    pass


class NotificationTemplate(TranslatableModel):
    type = models.CharField(max_length=50, verbose_name=_("type"), unique=True)

    from_email = models.EmailField(
        verbose_name=_("From email"), max_length=100, default=get_default_from_email
    )

    admins_to_notify = models.ManyToManyField(
        get_user_model(),
        related_name="+",
        blank=True,
        verbose_name=_("Admins to notify"),
        help_text=_(
            "Choose admin users you want to be notified when this event happens."
        ),
    )
    admin_notification_subject = models.CharField(
        verbose_name=_("admin notification subject"),
        max_length=200,
        help_text=_("Subject for admins' notification"),
        blank=True,
    )
    admin_notification_text = models.TextField(
        verbose_name=_("admin notification text"),
        help_text=_("Text body for admins' notification."),
        blank=True,
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
        if self.type in notifications.registry:
            return str(notifications.registry[self.type])
        else:
            return "{} ({})".format(self.type, _("disabled"))
