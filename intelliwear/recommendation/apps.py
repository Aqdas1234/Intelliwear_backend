from django.apps import AppConfig
#from recommendation.logic.singleton import get_cb_model

class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendation'
'''
    def ready(self):
        get_cb_model()
'''