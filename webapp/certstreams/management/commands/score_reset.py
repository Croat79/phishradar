from django.core.management.base import BaseCommand

from certstreams import models


class Command(BaseCommand):

    help = 'Resets scores for all domains'

    def handle(self, *args, **options):
        models.Domain.objects.update(score=None)
