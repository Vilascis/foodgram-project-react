from django.apps import AppConfig


class CookbookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.cookbook'
    label = 'core_cookbook'
    verbose_name = 'Приложение рецепты'
