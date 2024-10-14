"""Settings for the django_help app.

Use the DJANGO_HELP_CONFIG setting to configure the app. For example:

.. code-block:: python

    DJANGO_HELP_CONFIG = {
        "BASE_MANAGER": "myapp.models.MyManager",
        "BASE_QUERYSET": "myapp.models.MyQuerySet",
        "BASE_MODEL": "myapp.models.MyModel",
        "BASE_FOREIGN_KEY": "myapp.models.MyForeignKey",
        "EXTRA_LANGUAGES": {
            "es": {"blank": False},  # Spanish fields must be filled out.
            "fr": {"blank": True},  # French fields can be left blank.
        },
        "AUTHORIZE_USER_TO_VIEW_ARTICLE": "myapp.utils.authorize_user_to_view_article",
        "INTENDED_ENTITY_TYPE": {
            "PERSON": ("person", "Person"),
            "ORGANIZATION": ("organization", "Organization"),
        },
    }
"""

from django.conf import settings
from django.db import models

from django_help.utils.validation import user_authorized_to_view


django_help_config = getattr(settings, "DJANGO_HELP_CONFIG", {})

# Specifies the base form for all forms in the app.
BASE_MANAGER = django_help_config.get("BASE_MANAGER", models.Manager)

# Specifies the base queryset for all models in the app.
BASE_QUERYSET = django_help_config.get("BASE_QUERYSET", models.QuerySet)

# Specifies the base model for all models in the app.
BASE_MODEL = django_help_config.get("BASE_MODEL", models.Model)

# Specifies the model field for foreign keys in the app.
BASE_FOREIGN_KEY_FIELD = django_help_config.get("BASE_FOREIGN_KEY", models.ForeignKey)

# Specifies extra languages to use in the app.
EXTRA_LANGUAGES = django_help_config.get("EXTRA_LANGUAGES", {})

# A function for authorizing users to view articles.
# The function should take a request and an article as arguments and return True if the user is authorized to view the
# article, and False otherwise.
AUTHORIZE_USER_TO_VIEW_ARTICLE = django_help_config.get("AUTHORIZE_USER_TO_VIEW_ARTICLE", user_authorized_to_view)

# The default intended entity type for articles and categories.
# This is a tuple of the form (code, name).
# ("any", "Any") is the default value, which can be used as `IntendedEntityType.ANY`.
# This is optional, and can be used for filtering articles and categories by intended entity type.
# How you define the intended entity type is up to you.
INTENDED_ENTITY_TYPE = django_help_config.get("INTENDED_ENTITY_TYPE", {})
