from django.core.management.base import BaseCommand
from recommendation.logic.singleton import get_image_search_model


class Command(BaseCommand):
    help = 'Loads Image Search model'

    def handle(self, *args, **options):
        get_image_search_model()
        self.stdout.write(self.style.SUCCESS('Image Search model loaded successfully'))