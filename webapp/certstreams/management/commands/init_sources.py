from json import decoder

import requests

from django.core.management.base import BaseCommand

from certstreams import models


class Command(BaseCommand):

    help = 'Fetches sources'

    def handle(self, *args, **options):
        for src in models.Source.objects.all():
            url = '{}/ct/v1/get-sth'.format(src.url)
            try:
                response = requests.get(url).json()
            except (requests.ConnectionError, decoder.JSONDecodeError):
                src.broken = True
                self.stdout.write(self.style.SUCCESS('Initialization failed for {}'.format(src)))
            else:
                last_index = response['tree_size']
                if last_index:
                    src.last_index = last_index
                else:
                    src.broken = True
                self.stdout.write(self.style.SUCCESS('Initialized {} with last index value of {}'.format(src, src.last_index)))
            finally:
                src.save()
