import idna

from django.conf import settings

from certstreams import imports


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
        return idna.decode(value)


filters = []
for fil in settings.CERTSTREAMS_FILTERS:
    filters.append(imports.import_class(fil)())
