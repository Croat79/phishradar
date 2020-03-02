import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from certstreams import tasks


logger = logging.getLogger('app')


class Command(BaseCommand):

    help = 'Scores all available domains'

    def handle(self, *args, **options):
        result = tasks.score_all.apply_async(queue=settings.CERTSTREAMS_SCORING_QUEUE)
        logger.info(result)
