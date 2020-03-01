import math
import re

import tld

from django.conf import settings

from certstreams import (
    imports,
    models,
)


KEYWORDS = models.Keyword.objects.filter(partial=False).values_list('name', flat=True)
PARTIALS = models.Keyword.objects.filter(partial=True).values_list('name', flat=True)
TLDS = models.TLD.objects.all()


class Scoring:

    def score(self, domain):
        raise NotImplementedError

    def words(self, domain):
        result = tld.get_tld(domain, as_object=True, fail_silently=True, fix_protocol=True)
        if result:
            without_tld = '.'.join([result.subdomain, result.domain])
            words = re.split('\W+', without_tld)
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


class Dots(Scoring):

    def score(self, domain):
        return domain.count('.') * 2


class Dashes(Scoring):

    def score(self, domain):
        return domain.count('-') * 4


class Keywords(Scoring):

    def score(self, domain):
        score = 0
        words = self.words(domain)
        for keyword in KEYWORDS:
            if keyword in domain:
                score += 5
        for keyword in KEYWORDS:
            if keyword in words:
                score += 20
                words.remove(keyword)
        for partial in PARTIALS:
            for word in words:
                if partial in word:
                    score += 3
        return score


class Entropy(Scoring):

    def score(self, domain):
        prob = [float(domain.count(c)) / len(domain) for c in dict.fromkeys(list(domain))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return int(entropy * 10)


scoring = []
for scor in settings.CERTSTREAMS_SCORING:
    scoring.append(imports.import_class(scor)())
