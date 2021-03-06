import pytest
from django.conf import settings
from django.core import mail
from mailer.engine import send_all
from mailer.models import Message

from django_ilmoitin.models import NotificationTemplate, NotificationTemplateException
from django_ilmoitin.utils import render_notification_template, send_notification


def test_notification_template_rendering(notification_template):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }

    template = NotificationTemplate.objects.filter(type="event_created").first()

    rendered = render_notification_template(template, context, "en")
    assert len(rendered) == 3
    assert rendered.subject == "test subject, variable value: bar!"
    assert rendered.body_html == "<b>test body HTML</b>, variable value: html_baz!"
    assert rendered.body_text == "test body text, variable value: text_baz!"

    rendered = render_notification_template(template, context, "fi")
    assert len(rendered) == 3
    assert rendered.subject == "testiotsikko, muuttujan arvo: bar!"
    assert rendered.body_html == "<b>testihötömölöruumis</b>, muuttujan arvo: html_baz!"
    assert rendered.body_text == "testitekstiruumis, muuttujan arvo: text_baz!"


def test_notification_template_rendering_no_body_text_provided(notification_template):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }
    notification_template.set_current_language("fi")
    notification_template.body_text = ""
    notification_template.save()
    notification_template.set_current_language("en")
    notification_template.body_text = ""
    notification_template.save()

    template = NotificationTemplate.objects.filter(type="event_created").first()

    rendered = render_notification_template(template, context, "en")
    assert len(rendered) == 3
    assert rendered.subject == "test subject, variable value: bar!"
    assert rendered.body_html == "<b>test body HTML</b>, variable value: html_baz!"
    assert rendered.body_text == "test body HTML, variable value: html_baz!"

    rendered = render_notification_template(template, context, "fi")
    assert len(rendered) == 3
    assert rendered.subject == "testiotsikko, muuttujan arvo: bar!"
    assert rendered.body_html == "<b>testihötömölöruumis</b>, muuttujan arvo: html_baz!"
    assert rendered.body_text == "testihötömölöruumis, muuttujan arvo: html_baz!"


def test_undefined_rendering_context_variable(notification_template):
    context = {"extra_var": "foo", "subject_var": "bar", "body_text_var": "baz"}

    template = NotificationTemplate.objects.filter(type="event_created").first()

    with pytest.raises(NotificationTemplateException) as e:
        render_notification_template(template, context, "fi")
    assert "'body_html_var' is undefined" in str(e.value)


def test_notification_sending(notification_template):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }

    attachment = "test.txt", "foo bar", "text/plain"

    send_notification("foo@bar.fi", "event_created", context, "fi", [attachment])

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    subject = message.subject
    body_html = next(a[0] for a in message.alternatives if a[1] == "text/html")
    body_text = message.body

    assert message.to == ["foo@bar.fi"]
    assert message.from_email == settings.DEFAULT_FROM_EMAIL
    assert subject == "testiotsikko, muuttujan arvo: bar!"
    assert body_html == "<b>testihötömölöruumis</b>, muuttujan arvo: html_baz!"
    assert body_text == "testitekstiruumis, muuttujan arvo: text_baz!"
    assert message.attachments[0] == attachment


@pytest.mark.parametrize("language", ["fi", "en"])
def test_translated_from_email(notification_template, settings, language):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }
    settings.ILMOITIN_TRANSLATED_FROM_EMAIL = {"fi": "Yrjö <ilmoitin@example.com>"}

    send_notification("foo@bar.fi", "event_created", context, language)

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.from_email == settings.ILMOITIN_TRANSLATED_FROM_EMAIL.get(
        language, settings.DEFAULT_FROM_EMAIL
    )


def test_notification_delayed_sending(notification_template):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }
    # Override settings to use django-mailer email backend
    settings.EMAIL_BACKEND = "mailer.backend.DbBackend"
    settings.MAILER_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.ILMOITIN_QUEUE_NOTIFICATIONS = True

    send_notification("foo@bar.fi", "event_created", context, "fi")
    assert len(mail.outbox) == 0
    assert Message.objects.count() == 1
    # Now actually send emails
    Message.objects.retry_deferred()
    send_all()
    assert Message.objects.count() == 0
    assert len(mail.outbox) == 1
