from django.core.management.base import BaseCommand
from recommendation.logic.singleton import get_nlp_model


class Command(BaseCommand):
    help = 'Loads NLP model'

    def handle(self, *args, **options):
        get_nlp_model()
        self.stdout.write(self.style.SUCCESS('NLP model loaded successfully'))