import math
import re

import tld

from django.conf import settings

from certstreams import (
    imports,
    models,
)


KEYWORDS = models.Keyword.objects.filter(partial=False)
PARTIALS = models.Keyword.objects.filter(partial=True)
TLDS = models.TLD.objects.all().values_list('name', flat=True)


class Scoring:

    def score(self, domain):
        raise NotImplementedError

    def replace_multiple(self, char, value):
        return re.sub(char + '+', char, value)

    def words(self, domain):
        result = tld.get_tld(domain, as_object=True, fail_silently=True, fix_protocol=True)
        if result:
            without_tld = '.'.join([result.subdomain, result.domain])
            words = re.split(r'\W+', without_tld)
            return words
        else:
            return list()


class TLDs(Scoring):

    def score(self, domain):
        words = self.words(domain)
        for word in words:
            if word in TLDS:
                return 15
        return 0


class Char(Scoring):

    char = None
    weight = None

    def score(self, domain):
        purified = self.replace_multiple(self.char, domain)
        return purified.count(self.char) * self.weight


class Dots(Char):

    char = '.'
    weight = 2


class Dashes(Char):

    char = '-'
    weight = 4


class Keywords(Scoring):

    def score(self, domain):
        score = 0
        words = self.words(domain)
        for keyword in KEYWORDS:
            if keyword.matching_startswith:
                if domain.startswith(keyword.name):
                    score += keyword.weight
            elif keyword.matching_endswith:
                if domain.endswith(keyword.name):
                    score += keyword.weight
            elif keyword.name in words:
                score += keyword.weight
                words.remove(keyword.name)
        for partial in PARTIALS:
            for word in words:
                if partial.name in word:
                    score += partial.weight
        return score


class Entropy(Scoring):

    def score(self, domain):
        prob = [float(domain.count(c)) / len(domain) for c in dict.fromkeys(list(domain))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return int(entropy * 10)


scoring = []
for scor in settings.CERTSTREAMS_SCORING:
    scoring.append(imports.import_class(scor)())
