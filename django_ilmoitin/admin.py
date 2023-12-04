from django import forms
from django.contrib.admin import site as admin_site
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from .models import NotificationTemplate
from .registry import notifications
from .utils import render_preview


class NotificationTemplateForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Do not allow the admin to choose any of the template types that already
        # exist.
        existing_templates = NotificationTemplate.objects.all()
        if self.instance and self.instance.type:
            existing_templates = existing_templates.exclude(id=self.instance.id)
        used_types = set(existing_templates.values_list("type", flat=True))
        choices = [x for x in notifications.registry.items() if x[0] not in used_types]
        self.fields["type"] = forms.ChoiceField(choices=choices)

        admins_qs = (
            get_user_model()
            .objects.exclude(email="")
            .filter(Q(is_superuser=True) | Q(is_staff=True))
        )
        self.fields["admins_to_notify"].choices = [(a.id, a.email) for a in admins_qs]


class NotificationTemplateAdmin(TranslatableAdmin):
    form = NotificationTemplateForm
    change_form_template = "admin/preview_template.html"
    fieldsets = [
        (None, {"fields": ["type"]}),
        (_("User notification"), {"fields": ["subject", "body_html", "body_text"]}),
        (
            _("Admin notification"),
            {
                "fields": [
                    "admins_to_notify",
                    "admin_notification_subject",
                    "admin_notification_text",
                ]
            },
        ),
    ]

    def save_model(self, request, obj, form, change):
        if "_preview" not in request.POST:
            super(NotificationTemplateAdmin, self).save_model(
                request, obj, form, change
            )

    def response_change(self, request, obj):
        if "_preview" in request.POST:
            return self.preview(request, obj)
        else:
            return super(NotificationTemplateAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_preview" in request.POST:
            return self.preview(request, obj)
        else:
            return super(NotificationTemplateAdmin, self).response_add(
                request, obj, post_url_continue=None
            )

    def preview(self, request, obj, **kwargs):
        return HttpResponse(render_preview(obj))


admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
