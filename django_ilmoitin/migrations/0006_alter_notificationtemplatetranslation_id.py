# Generated by Django 3.2.18 on 2024-10-17 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_ilmoitin", "0005_bigauto_pk_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notificationtemplatetranslation",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
