import homoglyphs

from django.conf import settings


def generate_homoglyphs(keyword):
    hgl = homoglyphs.Homoglyphs(**settings.CERTSTREAMS_GENERATORS_HOMOGLYPHS)
    return hgl.get_combinations(keyword)
