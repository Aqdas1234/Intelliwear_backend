from django.apps import AppConfig


class AdminapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminApi'


    def ready(self):
        import adminApi.signals 


