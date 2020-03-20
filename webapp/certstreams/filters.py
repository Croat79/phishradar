import logging

import idna

from django.conf import settings

from certstreams import imports


logger = logging.getLogger('app')


class Filter:

    def filter(self, value):
        raise NotImplementedError


class RemoveWildcards(Filter):

    def filter(self, value):
        if value.startswith('*.'):
            return value[2:]
        else:
            return value


class DecodeIDNA(Filter):

    def filter(self, value):
        try:
            return idna.decode(value)
        except Exception as exc:
            logger.error(exc, ' = ', value)


filters = []
for fil in settings.CERTSTREAMS_FILTERS:
    filters.append(imports.import_class(fil)())
