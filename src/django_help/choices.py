"""This module contains the choices for the models in the django_help app."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_help.app_settings import INTENDED_ENTITY_TYPE


class IntendedEntityType(models.TextChoices):
    """Stores the type of entity that a category or article is intended for."""

    ANY = "any", _("Any")
    for key, (value, display) in INTENDED_ENTITY_TYPE.items():
        locals()[key] = (value, display)
