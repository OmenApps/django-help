"""App configuration for django-help."""

from django.apps import AppConfig


class DjangoHelpConfig(AppConfig):
    """App configuration for django-help."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_help"

    def ready(self):
        """Run when the app is ready."""
        from django_help import checks  # pylint: disable=C0415 disable=W0611
