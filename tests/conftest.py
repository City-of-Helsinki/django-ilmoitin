import pytest
from graphene import ObjectType, Schema
from graphene.test import Client
from parler.utils.context import switch_language

from django_ilmoitin.api.schema import Query
from django_ilmoitin.dummy_context import COMMON_CONTEXT, DummyContext
from django_ilmoitin.models import NotificationTemplate
from django_ilmoitin.registry import notifications


@pytest.fixture(autouse=True)
def autouse_django_db(db):
    pass


@pytest.fixture(autouse=True)
def force_settings(settings):
    settings.LANGUAGES = (("fi", "Finnish"), ("en", "English"))
    settings.LANGUAGE_CODE = "en"


@pytest.fixture
def notification_template():
    notification_type = "event_created"
    notifications.register(notification_type, "Event created")
    template = NotificationTemplate.objects.language("en").create(
        type=notification_type,
        subject="test subject, variable value: {{ subject_var }}!",
        body_html="<b>test body HTML</b>, variable value: {{ body_html_var }}!",
        body_text="test body text, variable value: {{ body_text_var }}!",
    )

    with switch_language(template, "fi"):
        template.subject = "testiotsikko, muuttujan arvo: {{ subject_var }}!"
        template.body_html = (
            "<b>testihötömölöruumis</b>, muuttujan arvo: {{ body_html_var }}!"
        )
        template.body_text = "testitekstiruumis, muuttujan arvo: {{ body_text_var }}!"
        template.save()

    dummy_context = DummyContext()
    dummy_context.update(
        {
            COMMON_CONTEXT: {},
            notification_type: {
                "subject_var": "subject",
                "body_html_var": "body_html_var",
                "body_text_var": "body_text_var",
            },
        }
    )

    return template


@pytest.fixture
def graphql_client():
    class SchemaQuery(Query, ObjectType):
        pass

    client = Client(schema=Schema(query=SchemaQuery))
    return client
