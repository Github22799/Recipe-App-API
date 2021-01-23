import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        db_conn = None
        fail_msg = 'Connection failed. Trying again after 1 second.'
        success_msg = 'Connected to database successfully.'

        self.stdout.write('Connecting to the database...')

        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write(fail_msg)
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS(success_msg))
