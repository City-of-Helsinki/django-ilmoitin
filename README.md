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
    ```
Use version 0.7.0 for a project based on Django >= 3.2 and Python >= 3.8

For older Python versions, use version 0.6.0.

Use version 0.5.x for a project based on Django 2.x.

If you need to make changes to `django-ilmoitin` and your project uses Django 2.x, add your changes to the branch [stable/0.5.x](https://github.com/City-of-Helsinki/django-ilmoitin/tree/stable/0.5.x) and then make a new 0.5.x release from it.

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
    DEFAULT_FROM_EMAIL = "Ilmoitin <ilmoitin@example.com>"
    ```
    In case you need translated from addresses, those can be defined like
    ```python
    ILMOITIN_TRANSLATED_FROM_EMAIL: {
       "fi": "Yrjö <ilmoitin@example.com>",
       "en": "George <ilmoitin@example.com>",
    }
    ```
    The value from `DEFAULT_FROM_EMAIL` will be used for languages not defined in that dict.

3. Create a `notifications.py` file in django app and register your notification types:

    ```python
    from django_ilmoitin.registry import notifications
    
    notifications.register("event_created", "Event created")
    notifications.register("event_deleted", "Event deleted")
    ```

4. Create a `dummy_context.py` file in django app and add dummy context data.
Either use the codes of notifications that you registered in the previous step, or
use the const `COMMON_CONTEXT` to make some variables available for all templates:

    ```python
    from django_ilmoitin.dummy_context import COMMON_CONTEXT, dummy_context
    
    from .models import MyModel
    
    my_object = MyModel(foo="bar")
    
    dummy_context.update({
        COMMON_CONTEXT: {"my_object": my_object},
        "event_created": {
            "foo": "bar"
        },
        "event_deleted": {
            "fizz": "buzz"
        }
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

7. Send notifications. List of attachment files can be passed as last optional argument:

    ```python
    from django_ilmoitin.utils import send_notification
    
    context = {
        "foo": "bar",
    }
    attachment = "test.txt", "foo bar", "text/plain"

    send_notification("foo@bar.com", "event_created", context, [attachment])
    
    ```

8. By default, notifications will be sent immediately, if you only want to add notification to the message queue
 and send it later, configure `ILMOITIN_QUEUE_NOTIFICATIONS`:
    ```python
    ILMOITIN_QUEUE_NOTIFICATIONS = True
    ```

## Using the GraphQL API
The package provides an optional GraphQL API that requires a working [graphene](https://graphene-python.org/) API
to work, and it needs additional dependencies.

1. To install them, run: `pip install django-ilmoitin[graphql_api]`

2. Add the `Query` to the entrypoint where you build your schema:

```python
# my_app/schema.py
import django_ilmoitin.api.schema as django_ilmoitin_schema

class Query(
    # other extended classes
    django_ilmoitin_schema.Query,
    graphene.ObjectType,
):
    pass

```

### Adding authentication to the queries
All the queries are public by default. The way to protect them is to override the resolvers on your app and call the "parent" query on the new resolver.

An example of how to protect a query would be as follows:
```python
class Query(
    # other extended classes
    django_ilmoitin_schema.Query,
    graphene.ObjectType,
):

  @staticmethod
  @login_required
  def resolve_notification_templates(parent, info, **kwargs):
      return django_ilmoitin_schema.Query.resolve_notification_templates(
          parent, info, **kwargs
      )
```

If you need more specific permission checking, you can also do
```python
class Query(
    # other extended classes
    django_ilmoitin_schema.Query,
    graphene.ObjectType,
):

  @staticmethod
  def resolve_notification_templates(parent, info, **kwargs):
      user = info.context.user
      if user.has_perms(["very_specific_permission"]):
          return django_ilmoitin_schema.Query.resolve_notification_templates(
              parent, info, **kwargs
          )
      raise PermissionError("User not authorised")
```


## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`


## Troubleshooting guide
1. Cannot receive email even though it was sent successfully

- Some strict spam filter might mark email as spam if its Message-ID header has suspicious domain name (e.g
 _158431519447.10.15335486611387428798@**qa-staging-i09m9b-staging-77bd999444-p2497**_) 
- This is because Python tries to generate messsage id base on the FQDN of the local machine before sending email
. Fortunately most of Email Sending services (Mailgun, MailChimp, Sendgrid,..) have a way to generate a reliable
 message-id that will likely pass spam filter, so we better let them do it.
- If you are using `django-anymail` as the email backend, there is an easy way to remove the auto-generated Message
 ID using `pre_send` signal
 
- Example:
  
```python
    from anymail.signals import pre_send
    @receiver(pre_send)
    def remove_message_id(sender, message, **kwargs):
        message.extra_headers.pop("Message-ID", None)
```


Note that it only works if you are using `django-anymail` as your email backend
