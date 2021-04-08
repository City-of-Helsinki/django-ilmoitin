# Generated by Django 3.0.8 on 2020-07-29 09:47

from django.db import migrations
import django.db.models.deletion
import parler.fields


class Migration(migrations.Migration):

    dependencies = [
        ("django_ilmoitin", "0003_remove_notificationtemplate_from_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationtemplatetranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="django_ilmoitin.NotificationTemplate",
            ),
        ),
    ]