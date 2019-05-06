from django.contrib.admin import site as admin_site
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm

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


admin_site.register(NotificationTemplate, NotificationTemplateAdmin)
