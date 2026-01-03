"""Django app configuration for options."""
from django.apps import AppConfig


class OptionsConfig(AppConfig):
    """Configuration for options app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.options'
    verbose_name = 'Options Data'

