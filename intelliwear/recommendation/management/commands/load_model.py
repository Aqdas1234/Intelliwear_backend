from django.core.management.base import BaseCommand
from recommendation.logic.singleton import get_cb_model,get_cf_model
import os
import csv

class Command(BaseCommand):
    help = 'Loads CBModel and conditionally loads CFModel if at least 10 entries exist in cf_data.csv'

    def handle(self, *args, **options):
        get_cb_model()
        get_cf_model()
        cf_data_path = 'recommendation/data/data.csv'
        '''
        if os.path.exists(cf_data_path):
            with open(cf_data_path, mode='r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None) 
                row_count = sum(1 for _ in reader)

            if row_count >= 10:
                get_cf_model()
                self.stdout.write(self.style.SUCCESS('CFModel loaded (10+ entries in cf_data.csv)'))
            else:
                self.stdout.write(self.style.WARNING('CFModel NOT loaded (less than 10 entries in cf_data.csv)'))
        else:
            self.stdout.write(self.style.ERROR('cf_data.csv not found'))
        '''
        self.stdout.write(self.style.SUCCESS('CBModel  and CFModel loaded successfully'))