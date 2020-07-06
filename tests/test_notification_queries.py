import pytest  # noqa
from graphql_relay import to_global_id

from django_ilmoitin.api.schema import NotificationTemplateNode
from django_ilmoitin.api.schema.types import LanguageEnum
from django_ilmoitin.utils import render_preview


def test_query_notification_templates(graphql_client, notification_template):
    query = """
    {
        notificationTemplates {
            edges {
                node {
                    id
                    preview
                    translations {
                        subject
                        languageCode
                        bodyHtml
                        bodyText
                        preview
                    }
                }
            }
        }
    }
    """
    executed = graphql_client.execute(query)
    notification_en = notification_template.translations.get(language_code="en")
    notification_fi = notification_template.translations.get(language_code="fi")

    expected_translations = [
        {
            "languageCode": LanguageEnum.get("en").name,
            "subject": notification_en.subject,
            "bodyHtml": notification_en.body_html,
            "bodyText": notification_en.body_text,
            "preview": render_preview(notification_template, "en"),
        },
        {
            "languageCode": LanguageEnum.get("fi").name,
            "subject": notification_fi.subject,
            "bodyHtml": notification_fi.body_html,
            "bodyText": notification_fi.body_text,
            "preview": render_preview(notification_template, "fi"),
        },
    ]
    translations = executed["data"]["notificationTemplates"]["edges"][0]["node"].pop(
        "translations"
    )

    for translation in translations:
        assert translation in expected_translations

    assert executed["data"]["notificationTemplates"]["edges"][0]["node"] == {
        "id": to_global_id(
            NotificationTemplateNode._meta.name, notification_template.id
        ),
        "preview": render_preview(notification_template),
    }
