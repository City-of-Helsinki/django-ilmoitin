from graphene_django import DjangoConnectionField

from .types import NotificationTemplateNode


class Query:
    notification_templates = DjangoConnectionField(NotificationTemplateNode)
