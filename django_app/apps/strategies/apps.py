"""Django app configuration for strategies."""
from django.apps import AppConfig


class StrategiesConfig(AppConfig):
    """Configuration for strategies app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.strategies'
    verbose_name = 'Strategy History'

