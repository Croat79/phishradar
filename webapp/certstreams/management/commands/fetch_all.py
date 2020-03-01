import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from certstreams import tasks


logger = logging.getLogger('app')


class Command(BaseCommand):

    help = 'Fetches certs for each source'

    def handle(self, *args, **options):
        result = tasks.fetch_all.apply_async(queue=settings.CERTSTREAMS_FETCHING_QUEUE)
        logger.info(result)
