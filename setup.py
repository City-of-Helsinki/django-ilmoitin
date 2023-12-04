import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django_ilmoitin",
    version="0.7.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    license="MIT License",
    description="Django app for sending notifications.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/City-of-Helsinki/django-ilmoitin",
    author="City of Helsinki",
    author_email="dev@hel.fi",
    install_requires=[
        "Django>=3.2",
        "django-parler>=2.0",
        "django-anymail",
        "django-mailer",
        "jinja2",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-django"],
    extras_require={
        "graphql_api": [
            "graphene>=2.0",
            "graphene-django",
            "graphql-core<3,>=2.1",
            "graphql-relay<3,>=2",
        ]
    },
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
