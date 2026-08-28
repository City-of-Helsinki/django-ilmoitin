import pytest
from django.contrib.auth.models import User
from django.core import mail
from mailer.engine import send_all
from mailer.models import Message

from django_ilmoitin.models import NotificationTemplate, NotificationTemplateException
from django_ilmoitin.utils import (
    render_notification_template,
    render_preview,
    send_notification,
)


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_notification_template_rendering():
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("language", "expected"),
    [
        ("en", "<b>test body HTML</b>, variable value: body_html_var!"),
        ("fi", "<b>testihötömölöruumis</b>, muuttujan arvo: body_html_var!"),
    ],
)
def test_render_preview_uses_dummy_context(notification_template, language, expected):
    assert render_preview(notification_template, language) == expected


@pytest.mark.django_db
def test_render_preview_uses_current_language(notification_template):
    notification_template.set_current_language("fi")

    assert (
        render_preview(notification_template)
        == "<b>testihötömölöruumis</b>, muuttujan arvo: body_html_var!"
    )


@pytest.mark.django_db
def test_render_preview_returns_template_error(notification_template):
    notification_template.set_current_language("en")
    notification_template.body_html = "{% if %}"
    notification_template.save()

    preview = render_preview(notification_template, "en")

    assert "Expected an expression" in preview


@pytest.mark.django_db
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


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_undefined_rendering_context_variable():
    context = {"extra_var": "foo", "subject_var": "bar", "body_text_var": "baz"}

    template = NotificationTemplate.objects.filter(type="event_created").first()

    with pytest.raises(NotificationTemplateException) as e:
        render_notification_template(template, context, "fi")
    assert "'body_html_var' is undefined" in str(e.value)


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_notification_sending(settings):
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


@pytest.mark.usefixtures("notification_template")
@pytest.mark.parametrize("language", ["fi", "en"])
@pytest.mark.django_db
def test_translated_from_email(settings, language):
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


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_notification_delayed_sending(settings):
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


@pytest.mark.django_db
def test_send_notification_does_not_send_if_no_template(caplog):
    send_notification("john.doe@test.test", "nonexistent")

    assert len(mail.outbox) == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert (
        'No notification template created for "nonexistent"'
        in caplog.records[0].message
    )


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_send_notification_does_not_send_on_render_error(monkeypatch, caplog):
    def mock_render_notification_template(*_, **__):
        raise NotificationTemplateException("bonjour")

    monkeypatch.setattr(
        "django_ilmoitin.utils.render_notification_template",
        mock_render_notification_template,
    )

    send_notification("john.doe@test.test", "event_created")

    assert len(mail.outbox) == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "bonjour"


@pytest.mark.usefixtures("notification_template")
@pytest.mark.django_db
def test_send_notification_does_not_if_subject_is_missing(monkeypatch, caplog):
    def mock_render_notification_template(*_, **__):
        return "", "body_html", "body_text"

    monkeypatch.setattr(
        "django_ilmoitin.utils.render_notification_template",
        mock_render_notification_template,
    )

    send_notification("john.doe@test.test", "event_created")

    assert len(mail.outbox) == 0
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "empty subject" in caplog.records[0].message


@pytest.mark.django_db
def test_send_notification_notify_admins(notification_template):
    context = {
        "extra_var": "foo",
        "subject_var": "bar",
        "body_html_var": "html_baz",
        "body_text_var": "text_baz",
    }
    admin_user_1 = User.objects.create_user("admin1", email="admin1@test.test")
    admin_user_2 = User.objects.create_user("admin2", email="admin2@test.test")

    notification_template.admin_notification_subject = "admin_subject"
    notification_template.admin_notification_text = "admin_text"
    notification_template.admins_to_notify.add(admin_user_1, admin_user_2)
    notification_template.save()
    send_notification("john.doe@test.test", "event_created", context, "fi")

    # Should have sent notification + two admin notifications in outbox
    assert len(mail.outbox) == 3
    sent_notification = mail.outbox[0]
    assert "testiotsikko" in sent_notification.subject
    for i, sent_admin_notification in enumerate(mail.outbox[1:]):
        assert sent_admin_notification.subject == "admin_subject"
        assert sent_admin_notification.body == "admin_text"
        assert len(sent_admin_notification.to) == 1
        assert sent_admin_notification.to[0] == f"admin{i + 1}@test.test"
