import pytest

from django_ilmoitin.models import NotificationTemplate
from django_ilmoitin.registry import notifications


@pytest.fixture(autouse=True)
def autouse_django_db(db):
    pass


@pytest.fixture
def notification_template(settings):
    settings.LANGUAGES = (("fi", "Finnish"), ("en", "English"))
    notifications.register("event_created", "Event created")
    notifications.register("event_approved", "Event approved")
    template = NotificationTemplate.objects.language("en").create(
        type="event_created",
        subject="test subject, variable value: {{ subject_var }}!",
        body_html="<b>test body HTML</b>, variable value: {{ body_html_var }}!",
        body_text="test body text, variable value: {{ body_text_var }}!",
    )
    template.set_current_language("fi")
    template.subject = "testiotsikko, muuttujan arvo: {{ subject_var }}!"
    template.body_html = (
        "<b>testihötömölöruumis</b>, muuttujan arvo: {{ body_html_var }}!"
    )
    template.body_text = "testitekstiruumis, muuttujan arvo: {{ body_text_var }}!"

    template.save()

    return template
