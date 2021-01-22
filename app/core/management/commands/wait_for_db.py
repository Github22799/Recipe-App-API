import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        db_conn = None
        self.stdout.write('Connecting to the database...')
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Connection failed. Trying again after 1 second.')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Connected to database successfully.'))
