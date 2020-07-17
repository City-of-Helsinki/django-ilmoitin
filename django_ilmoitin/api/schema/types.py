import graphene
from django.apps import apps
from django.conf import settings
from graphene_django import DjangoObjectType
from parler.utils.context import switch_language

from django_ilmoitin.models import NotificationTemplate
from django_ilmoitin.utils import render_preview

LanguageEnum = graphene.Enum(
    "NotificationTemplateLanguage",
    [(lang[0].upper(), lang[0]) for lang in settings.LANGUAGES],
)


class NotificationTranslationType(DjangoObjectType):
    language_code = LanguageEnum(required=True)
    subject = graphene.String()
    body_html = graphene.String()
    body_text = graphene.String()
    preview = graphene.String()

    class Meta:
        model = apps.get_model("django_ilmoitin", "NotificationTemplateTranslation")
        exclude = ("id", "master")

    def resolve_preview(self, info):
        with switch_language(self.master, self.language_code):
            return render_preview(self.master)


class NotificationTemplateNode(DjangoObjectType):
    type = graphene.String(required=True)
    translations = graphene.List(NotificationTranslationType, required=True)
    preview = graphene.String()

    class Meta:
        model = NotificationTemplate
        interfaces = (graphene.relay.Node,)
        exclude = (
            "admins_to_notify",
            "admin_notification_subject",
            "admin_notification_text",
        )

    def resolve_translations(self, info):
        return self.translations.all()

    def resolve_preview(self, info):
        return render_preview(self)
