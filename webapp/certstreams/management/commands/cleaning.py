import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from certstreams import tasks


logger = logging.getLogger('app')


class Command(BaseCommand):

    help = 'Cleans up low-scored and oldish domains'

    def handle(self, *args, **options):
        result = tasks.cleaning.apply_async(queue=settings.CERTSTREAMS_UTILITY_QUEUE)
        logger.info(result)
