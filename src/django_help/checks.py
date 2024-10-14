"""Checks for the django-help package."""

from django.conf import settings
from django.core.checks import Info
from django.core.checks import Warning
from django.core.checks import register
from django.db import models

from django_help import app_settings


@register()
def check_extra_languages_in_settings(app_configs, **kwargs):  # pylint: disable=W0613  # pylint: disable=W0613
    """Check that languages in EXTRA_LANGUAGES are available in settings.LANGUAGES."""

    errors = []
    available_languages = dict(settings.LANGUAGES)

    for lang_code in app_settings.EXTRA_LANGUAGES:
        if lang_code not in available_languages:
            errors.append(
                Warning(
                    f"Language '{lang_code}' specified in EXTRA_LANGUAGES is not available in " "settings.LANGUAGES.",
                    hint="Add the language to settings.LANGUAGES or remove it from EXTRA_LANGUAGES.",
                    id="django_help.W001",
                )
            )

    return errors


@register()
def check_languages_in_extra_languages(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that languages in settings.LANGUAGES are specified in EXTRA_LANGUAGES except for LANGUAGE_CODE."""

    messages = []
    available_languages = dict(settings.LANGUAGES)

    for lang_code, lang_name in available_languages.items():
        if lang_code not in app_settings.EXTRA_LANGUAGES and lang_code != settings.LANGUAGE_CODE:
            messages.append(
                Info(
                    f"Language '{lang_code}' ({lang_name}) from settings.LANGUAGES is not specified in "
                    "EXTRA_LANGUAGES.",
                    hint="Consider adding the language to EXTRA_LANGUAGES if it should be translatable.",
                    id="django_help.I001",
                )
            )

    return messages


@register()
def check_authorize_user_to_view_article(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that AUTHORIZE_USER_TO_VIEW_ARTICLE is a callable."""
    errors = []
    authorize_user_to_view_article = app_settings.AUTHORIZE_USER_TO_VIEW_ARTICLE

    if not callable(authorize_user_to_view_article):
        errors.append(
            Warning(
                "AUTHORIZE_USER_TO_VIEW_ARTICLE is not a callable.",
                hint="AUTHORIZE_USER_TO_VIEW_ARTICLE should be a callable function that takes a request and "
                "an article as arguments.",
                id="django_help.W002",
            )
        )

    return errors


@register()
def check_intended_entity_type(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that INTENDED_ENTITY_TYPE is a dictionary."""
    errors = []
    intended_entity_type = app_settings.INTENDED_ENTITY_TYPE

    if not isinstance(intended_entity_type, dict):
        errors.append(
            Warning(
                "INTENDED_ENTITY_TYPE is not a dictionary.",
                hint="INTENDED_ENTITY_TYPE should be a dictionary of intended entity types.",
                id="django_help.W003",
            )
        )

    return errors


@register()
def check_base_manager(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that BASE_MANAGER is a subclass of django.db.models.Manager."""
    errors = []
    base_manager = app_settings.BASE_MANAGER

    if not issubclass(base_manager, models.Manager):
        errors.append(
            Warning(
                "BASE_MANAGER is not a subclass of django.db.models.Manager.",
                hint="BASE_MANAGER should be a subclass of django.db.models.Manager.",
                id="django_help.W004",
            )
        )

    return errors


@register()
def check_base_queryset(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that BASE_QUERYSET is a subclass of django.db.models.QuerySet."""
    errors = []
    base_queryset = app_settings.BASE_QUERYSET

    if not issubclass(base_queryset, models.QuerySet):
        errors.append(
            Warning(
                "BASE_QUERYSET is not a subclass of django.db.models.QuerySet.",
                hint="BASE_QUERYSET should be a subclass of django.db.models.QuerySet.",
                id="django_help.W005",
            )
        )

    return errors


@register()
def check_base_model(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that BASE_MODEL is a subclass of django.db.models.Model."""
    errors = []
    base_model = app_settings.BASE_MODEL

    if not issubclass(base_model, models.Model):
        errors.append(
            Warning(
                "BASE_MODEL is not a subclass of django.db.models.Model.",
                hint="BASE_MODEL should be a subclass of django.db.models.Model.",
                id="django_help.W006",
            )
        )

    return errors


@register()
def check_base_foreign_key(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that BASE_FOREIGN_KEY is a subclass of django.db.models.ForeignKey."""
    errors = []
    base_foreign_key = app_settings.BASE_FOREIGN_KEY_FIELD

    if not issubclass(base_foreign_key, models.ForeignKey):
        errors.append(
            Warning(
                "BASE_FOREIGN_KEY is not a subclass of django.db.models.ForeignKey.",
                hint="BASE_FOREIGN_KEY should be a subclass of django.db.models.ForeignKey.",
                id="django_help.W007",
            )
        )

    return errors


@register()
def check_extra_languages(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that EXTRA_LANGUAGES is a dictionary."""
    errors = []
    extra_languages = app_settings.EXTRA_LANGUAGES

    if not isinstance(extra_languages, dict):
        errors.append(
            Warning(
                "EXTRA_LANGUAGES is not a dictionary.",
                hint="EXTRA_LANGUAGES should be a dictionary of extra languages.",
                id="django_help.W008",
            )
        )

    return errors


@register()
def check_extra_languages_values(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that values in EXTRA_LANGUAGES are dictionaries."""
    errors = []
    extra_languages = app_settings.EXTRA_LANGUAGES

    for lang_code, lang_settings in extra_languages.items():
        if not isinstance(lang_settings, dict):
            errors.append(
                Warning(
                    f"Value for language '{lang_code}' in EXTRA_LANGUAGES is not a dictionary.",
                    hint="Values in EXTRA_LANGUAGES should be dictionaries.",
                    id="django_help.W009",
                )
            )

    return errors


@register()
def check_extra_languages_values_keys(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that keys in EXTRA_LANGUAGES values are valid."""
    errors = []
    extra_languages = app_settings.EXTRA_LANGUAGES

    for lang_code, lang_settings in extra_languages.items():
        for key in lang_settings:
            if key not in ("blank",):
                errors.append(
                    Warning(
                        f"Invalid key '{key}' in EXTRA_LANGUAGES value for language '{lang_code}'.",
                        hint="Valid keys are 'blank'.",
                        id="django_help.W010",
                    )
                )

    return errors


@register()
def check_extra_languages_values_blank(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that 'blank' key in EXTRA_LANGUAGES values is a boolean."""
    errors = []
    extra_languages = app_settings.EXTRA_LANGUAGES

    for lang_code, lang_settings in extra_languages.items():
        blank = lang_settings.get("blank")

        if not isinstance(blank, bool):
            errors.append(
                Warning(
                    f"Value for 'blank' key in EXTRA_LANGUAGES value for language '{lang_code}' is not a " "boolean.",
                    hint="'blank' should be a boolean.",
                    id="django_help.W011",
                )
            )

    return errors


@register()
def check_intended_entity_type_values(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that values in INTENDED_ENTITY_TYPE are tuples."""
    errors = []
    intended_entity_type = app_settings.INTENDED_ENTITY_TYPE

    for entity_type, entity_settings in intended_entity_type.items():
        if not isinstance(entity_settings, tuple):
            errors.append(
                Warning(
                    f"Value for entity type '{entity_type}' in INTENDED_ENTITY_TYPE is not a tuple.",
                    hint="Values in INTENDED_ENTITY_TYPE should be tuples.",
                    id="django_help.W012",
                )
            )

    return errors


@register()
def check_intended_entity_type_values_length(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that values in INTENDED_ENTITY_TYPE tuples have a length of 2."""
    errors = []
    intended_entity_type = app_settings.INTENDED_ENTITY_TYPE

    for entity_type, entity_settings in intended_entity_type.items():
        if len(entity_settings) != 2:
            errors.append(
                Warning(
                    f"Value for entity type '{entity_type}' in INTENDED_ENTITY_TYPE does not have a length " "of 2.",
                    hint="Values in INTENDED_ENTITY_TYPE should have a length of 2.",
                    id="django_help.W013",
                )
            )

    return errors


@register()
def check_intended_entity_type_values_types(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that values in INTENDED_ENTITY_TYPE tuples are strings."""
    errors = []
    intended_entity_type = app_settings.INTENDED_ENTITY_TYPE

    for entity_type, entity_settings in intended_entity_type.items():
        if not all(isinstance(value, str) for value in entity_settings):
            errors.append(
                Warning(
                    f"Values for entity type '{entity_type}' in INTENDED_ENTITY_TYPE are not strings.",
                    hint="Values in INTENDED_ENTITY_TYPE should be strings.",
                    id="django_help.W014",
                )
            )

    return errors


@register()
def check_intended_entity_type_values_unique(app_configs, **kwargs):  # pylint: disable=W0613
    """Check that values in INTENDED_ENTITY_TYPE tuples are unique."""
    errors = []
    intended_entity_type = app_settings.INTENDED_ENTITY_TYPE
    values = [value for _, value in intended_entity_type.values()]

    if len(values) != len(set(values)):
        errors.append(
            Warning(
                "Values in INTENDED_ENTITY_TYPE tuples are not unique.",
                hint="Values in INTENDED_ENTITY_TYPE should be unique.",
                id="django_help.W015",
            )
        )

    return errors
