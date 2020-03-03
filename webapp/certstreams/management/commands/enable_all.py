from django.core.management.base import BaseCommand

from certstreams import models


class Command(BaseCommand):

    help = 'Enables all sources'

    def handle(self, *args, **options):
        models.Source.objects.update(enabled=True)
