from django.contrib.admin import site as admin_site
from django.http import HttpResponse
from jinja2 import DebugUndefined, TemplateSyntaxError
from jinja2.sandbox import SandboxedEnvironment
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

from .dummy_context import dummy_context
from .models import NotificationTemplate


class NotificationTemplateForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Do not allow the admin to choose any of the template types that already
        # exist.
        existing_templates = NotificationTemplate.objects.all()
        if self.instance and self.instance.type:
            existing_templates = existing_templates.exclude(id=self.instance.id)
        used_types = set(existing_templates.values_list("_type", flat=True))
        choices = [x for x in self.fields["_type"].choices if x[0] not in used_types]
        self.fields["_type"].choices = choices


class NotificationTemplateAdmin(TranslatableAdmin):
    form = NotificationTemplateForm
    change_form_template = "admin/preview_template.html"

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
        env = SandboxedEnvironment(
            trim_blocks=True, lstrip_blocks=True, undefined=DebugUndefined
        )
        try:
            body_html = env.from_string(obj.body_html).render(dummy_context.context)
            return HttpResponse(body_html)
        except TemplateSyntaxError as e:
            return HttpResponse(e)


admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
