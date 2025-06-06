from django.apps import AppConfig


class CustomerapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customerApi'

    def ready(self):
        import customerApi.signals
