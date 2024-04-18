from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.api'
    label = 'core_api'
    verbose_name = 'Приложение API'
