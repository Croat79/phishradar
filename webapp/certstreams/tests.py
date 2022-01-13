from django.test import TestCase

from certstreams import filters
from certstreams.tasks import filter_domains


class FiltersTestCase(TestCase):

    def test_filter_wildcards(self):
        fil = filters.RemoveWildcards()
        self.assertTrue(
            fil.exclude('*.example.com')
        )
        self.assertFalse(
            fil.exclude('example.com')
        )

    def test_filter_domains(self):
        domains = ('*.example.com', 'example.com')
        self.assertListEqual(
            filter_domains(domains),
            ['example.com']
        )
