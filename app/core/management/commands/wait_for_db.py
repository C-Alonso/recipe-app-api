import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


# Remember to add the real wait_for_db command to the docker-compose file.
class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    # Here we define what the Command will do when it's run.
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
