import requests

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from certstreams import models


class Command(BaseCommand):

    help = 'Fetches sources'

    def handle(self, *args, **options):
        ct_logs = requests.get(settings.CERTSTREAMS_LOGS_SOURCE).json()['logs']
        ct_logs_clean = [log['url'][:-1] for log in ct_logs if log['url'].endswith('/')]
        ct_logs_valid = [log for log in ct_logs_clean if log not in settings.CERTSTREAMS_LOGS_IGNORED]
        for log in ct_logs_valid:
            try:
                obj = models.Source.objects.create(url='https://{}'.format(log))
            except IntegrityError:
                self.stdout.write(self.style.ERROR('Source {} already exists'.format(log)))
            else:
                self.stdout.write(self.style.SUCCESS('Fetched {}'.format(obj)))
