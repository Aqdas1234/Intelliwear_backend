from django.core.management.base import BaseCommand
from recommendation.logic.singleton import get_cb_model

class Command(BaseCommand):
    help = 'Loads CBModel once without performing any task'

    def handle(self, *args, **options):
        get_cb_model()  
        self.stdout.write(self.style.SUCCESS('CBModel loaded successfully'))