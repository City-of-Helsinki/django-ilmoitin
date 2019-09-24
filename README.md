# django-ilmoitin

[![Latest PyPI version](https://badge.fury.io/py/django-ilmoitin.svg)](https://pypi.python.org/pypi/django-ilmoitin)
[![Python versions](https://img.shields.io/pypi/pyversions/django-ilmoitin.svg)](https://pypi.python.org/pypi/django-ilmoitin)

A templated Django messaging library

# Installation

1. `pip install django-ilmoitin`

2. Add `django_ilmoitin` to `INSTALLED_APPS`.

3. Run migrations

    ```python
    python manage.py migrate ilmoitin

# Usage

1. `django-ilmoitin` uses [`django-mailer`](https://github.com/pinax/django-mailer)
to send emails, so you need to configure the `MAILER_EMAIL_BACKEND` setting to let
[`django-mailer`](https://github.com/pinax/django-mailer) know, how to actually
send the mail:

    ```python
    MAILER_EMAIL_BACKEND = "your.actual.EmailBackend"
    ```

2. Define default from address in settings

    ```python
    DEFAULT_FROM_EMAIL = "your.email@address"
    ```

3. Create a `notifications.py` file in django app and register your notification types:

    ```python
    from django_ilmoitin.registry import notifications
    
    notifications.register("event_created", "Event created")
    ```

4. Create a `dummy_context.py` file in django app and add dummy context data:

    ```python
    from django_ilmoitin.dummy_context import dummy_context
    
    from .models import MyModel
    
    model = MyModel(foo="bar")
    
    dummy_context.context.update({
        "model": model
    })
    ```

5. Import notifications and dummy context in your apps.py:

    ```python
    from django.apps import AppConfig
    
    
    class ExampleConfig(AppConfig):
        name = "example"

        def ready(self):
            import example.notifications
            import example.dummy_context
    ```

6. Go to django admin and add notification templates to your notifications

7. Send notifications:

    ```python
    from django_ilmoitin.utils import send_notification
    
    context = {
        "foo": "bar",
    }
    send_notification("foo@bar.com", "event_created", context)
    
    ```

## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`
