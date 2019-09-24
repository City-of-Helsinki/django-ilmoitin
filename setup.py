import os

from setuptools import find_packages, setup

from django_ilmoitin import __version__

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django_ilmoitin",
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="Django app for sending notifications.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/City-of-Helsinki/django-ilmoitin",
    author="City of Helsinki",
    author_email="dev@hel.fi",
    install_requires=[
        "Django",
        "django-parler<2.0",
        "django-anymail",
        "django-mailer",
        "jinja2",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-django"],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
