import logging
from collections import namedtuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from jinja2 import DebugUndefined, StrictUndefined
from jinja2.exceptions import TemplateError
from jinja2.sandbox import SandboxedEnvironment
from mailer.engine import send_all
from mailer.models import Message
from parler.utils.context import switch_language

from .dummy_context import dummy_context
from .models import NotificationTemplate, NotificationTemplateException

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = settings.LANGUAGES[0][0]

RenderedTemplate = namedtuple("RenderedTemplate", ("subject", "body_html", "body_text"))


def send_notification(
    email, notification_type, context=None, language=DEFAULT_LANGUAGE, attachments=None
):
    logger.debug(
        'Trying to send notification "{}" to {}.'.format(notification_type, email)
    )

    if context is None:
        context = {}

    template = NotificationTemplate.objects.filter(type=notification_type).first()

    if not template:
        logger.warning(
            'No notification template created for "{}" event, not sending anything.'.format(
                notification_type
            )
        )
        return

    try:
        subject, body_html, body_text = render_notification_template(
            template, context, language
        )
    except NotificationTemplate.DoesNotExist:
        logger.debug(
            'NotificationTemplate "{}" does not exist, not sending anything.'.format(
                notification_type
            )
        )
        return
    except NotificationTemplateException as e:
        logger.error(e, exc_info=True)
        return

    if not subject:
        logger.warning(
            'Rendered notification "{}" has an empty subject, not sending anything.'.format(
                notification_type
            )
        )
        return

    if language in getattr(settings, "ILMOITIN_TRANSLATED_FROM_EMAIL", {}):
        from_email = settings.ILMOITIN_TRANSLATED_FROM_EMAIL[language]
    else:
        from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject,
        body_text,
        email,
        from_email=from_email,
        body_html=body_html,
        attachments=attachments,
    )

    if (
        template.admins_to_notify.exists()
        and template.admin_notification_subject
        and template.admin_notification_text
    ):
        admin_subject = template.admin_notification_subject
        admin_text = template.admin_notification_text

        for admin in template.admins_to_notify.all():
            send_mail(admin_subject, admin_text, admin.email, from_email=from_email)

    # Immediately fire django-mailer's commands if delayed=False
    if not getattr(settings, "ILMOITIN_QUEUE_NOTIFICATIONS", False):
        Message.objects.retry_deferred()
        send_all()


def render_notification_template(template, context, language_code=DEFAULT_LANGUAGE):
    """
    Render a notification template with given context in given language

    Returns a namedtuple containing all content fields (subject, body_html, body_text) of the template.
    """
    env = SandboxedEnvironment(
        trim_blocks=True, lstrip_blocks=True, undefined=StrictUndefined
    )

    with switch_language(template, language_code):
        try:
            subject = env.from_string(template.subject).render(context)
            body_html = env.from_string(template.body_html).render(context)

            if template.body_text:
                body_text = env.from_string(template.body_text).render(context)
            else:
                body_text = strip_tags(body_html)

            return RenderedTemplate(subject, body_html, body_text)

        except TemplateError as e:
            raise NotificationTemplateException(e) from e


def send_mail(
    subject,
    body_text,
    to_address,
    from_email=settings.DEFAULT_FROM_EMAIL,
    body_html=None,
    attachments=None,
):
    logger.info('Sending notification email to {}: "{}"'.format(to_address, subject))

    msg = EmailMultiAlternatives(
        subject, body_text, from_email, [to_address], attachments=attachments
    )
    if body_html:
        msg.attach_alternative(body_html, "text/html")

    msg.send()


def render_preview(
    notification_template: NotificationTemplate, lang: str = None
) -> str:
    """
    Return a rendered preview of the passed template and the values from the dummy context

    If no lang is passed, the current Django language.

    :param notification_template: The template to preview
    :param lang: The language for the preview
    :return: The rendered preview as string
    """
    env = SandboxedEnvironment(
        trim_blocks=True, lstrip_blocks=True, undefined=DebugUndefined
    )
    try:
        with switch_language(notification_template, language_code=lang):
            body_html = env.from_string(notification_template.body_html).render(
                dummy_context.get(notification_template.type)
            )
        return body_html
    except TemplateError as e:
        return str(e)
