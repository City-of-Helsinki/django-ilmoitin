from graphene_django import DjangoConnectionField

from django_ilmoitin.models import NotificationTemplate

from .types import NotificationTemplateNode


class Query:
    notification_templates = DjangoConnectionField(NotificationTemplateNode)

    @staticmethod
    def resolve_notification_templates(parent, info, **kwargs):
        return NotificationTemplate.objects.all()
