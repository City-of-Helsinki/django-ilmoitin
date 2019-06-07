import logging
from collections import namedtuple

from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.utils.html import strip_tags
from jinja2 import StrictUndefined
from jinja2.exceptions import TemplateError
from jinja2.sandbox import SandboxedEnvironment
from mailer.engine import send_all
from mailer.models import Message
from parler.utils.context import switch_language

from .models import NotificationTemplate, NotificationTemplateException

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = settings.LANGUAGES[0][0]

RenderedTemplate = namedtuple("RenderedTemplate", ("subject", "body_html", "body_text"))


def send_notification(
    email, notification_type, context=None, language=DEFAULT_LANGUAGE
):
    logger.debug(
        'Trying to send notification "{}" to {}.'.format(notification_type, email)
    )

    if context is None:
        context = {}

    try:
        subject, body_html, body_text = render_notification_template(
            notification_type, context, language
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

    send_mail(subject, body_html, body_text, email)

    # also immediately fire django-mailer's commands
    Message.objects.retry_deferred()
    send_all()


def render_notification_template(
    notification_type, context, language_code=DEFAULT_LANGUAGE
):
    """
    Render a notification template with given context in given language

    Returns a namedtuple containing all content fields (subject, body_html, body_text) of the template.
    """
    template = NotificationTemplate.objects.get(_type=notification_type)
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


def send_mail(subject, body_html, body_text, to_address):
    logger.info('Sending notification email to {}: "{}"'.format(to_address, subject))
    django_send_mail(
        subject,
        body_text,
        settings.DEFAULT_FROM_EMAIL,
        [to_address],
        html_message=body_html,
    )
