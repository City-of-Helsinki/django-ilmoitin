DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = ("django_ilmoitin", "tests", "mailer")

MIDDLEWARE = []

SITE_ID = 1
ROOT_URLCONF = "tests.urls"
DEBUG = True
USE_TZ = True
SECRET_KEY = "sekret"
