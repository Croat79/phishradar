import base64
import logging

from celery import shared_task
from OpenSSL import crypto
import construct
import requests

from django.conf import settings
from django.db import transaction
from django.db.models import F

from certstreams import (
    filters,
    models,
    scoring,
)


logger = logging.getLogger('app')


construct.MerkleTreeHeader = construct.Struct(
    'Version'         / construct.Byte,  # noqa
    'MerkleLeafType'  / construct.Byte,  # noqa
    'Timestamp'       / construct.Int64ub,  # noqa
    'LogEntryType'    / construct.Enum(construct.Int16ub, X509LogEntryType=0, PrecertLogEntryType=1),  # noqa
    'Entry'           / construct.GreedyBytes  # noqa
)

Certificate = construct.Struct(
    'Length' / construct.Int24ub,
    'CertData' / construct.Bytes(construct.this.Length)
)

CertificateChain = construct.Struct(
    'ChainLength' / construct.Int24ub,
    'Chain' / construct.GreedyRange(Certificate),
)


def filter_domains(domains):
    result = dict()
    for domain in domains:
        filtered = domain
        for fil in filters.filters:
            filtered = fil.filter(filtered)
        result[domain] = filtered
    return result


def dump_extensions(cert):
    extensions = dict()
    for x in range(cert.get_extension_count()):
        extension_name = ''
        try:
            extension_name = cert.get_extension(x).get_short_name()
            if extension_name == b'UNDEF':
                continue
            extensions[extension_name.decode('latin-1')] = cert.get_extension(x).__str__()
        except:
            extensions[extension_name.decode('latin-1')] = 'NULL'
    return extensions


def serialize_certificate(cert):
    subject = cert.get_subject()
    extensions = dump_extensions(cert)
    subject_alt_names = extensions.get('subjectAltName')
    domains = []
    if subject.CN:
        domains.append(subject.CN)
    if subject_alt_names:
        for entry in subject_alt_names.split(', '):
            if entry.startswith('DNS:'):
                entry = entry.replace('DNS:', '')
                if entry:
                    domains.append(entry)
    domains = filter_domains(set(domains))
    return {
        'domains': domains,
        'serial_number': '{0:x}'.format(int(cert.get_serial_number())),
        'fingerprint': str(cert.digest('sha1'), 'utf-8'),
        'issuer': dict(cert.get_issuer().get_components())[b'CN'],
    }


@shared_task
def fetch_entries(url, source_id):
    try:
        response = requests.get(url).json()
    except Exception as exc:
        logger.error('Failed to fetch {} due to {}'.format(url, exc))
    else:
        if 'entries' in response:
            objs = []
            for entry in response['entries']:
                mtl = construct.MerkleTreeHeader.parse(base64.b64decode(entry['leaf_input']))
                if mtl.LogEntryType == 'X509LogEntryType':
                    cert_data = serialize_certificate(crypto.load_certificate(crypto.FILETYPE_ASN1, Certificate.parse(mtl.Entry).CertData))
                    for original, filtered in cert_data['domains'].items():
                        logger.debug('Fetched: {} ({})'.format(filtered, original))
                        issuer, _ = models.Issuer.objects.get_or_create(name=cert_data['issuer'].decode('utf-8'))
                        objs.append(models.Domain(
                            source_id=source_id,
                            name_original=original,
                            name_filtered=filtered,
                            fingerprint=cert_data['fingerprint'],
                            serial_number=cert_data['serial_number'],
                            issuer_id=issuer.id,
                        ))
            models.Domain.objects.bulk_create(objs)


@shared_task
def fetch_source(source_id):
    src = models.Source.objects.get(pk=source_id)
    url = '{}/ct/v1/get-sth'.format(src.url)
    response = requests.get(url).json()
    tree_size = response['tree_size']
    last_index = src.last_index
    for idx in range(last_index, tree_size, settings.CERTSTREAMS_PAGING_STEP):
        query_url = '{}/ct/v1/get-entries?start={}&end={}'.format(src.url, idx, idx + settings.CERTSTREAMS_PAGING_STEP)
        fetch_entries.apply_async(queue=settings.CERTSTREAMS_FETCHING_QUEUE, args=(query_url, source_id))
    src.last_index = tree_size
    src.save()


@shared_task
def score_domains(domain_pks):
    domains = list(models.Domain.objects.filter(pk__in=domain_pks))
    with transaction.atomic():
        for domain in domains:
            domain.score = 0
            for scor in scoring.scoring:
                domain.score += scor.score(domain.name_filtered)
            domain.save()
    return len(domains)


@shared_task
def fetch_all():
    for src in models.Source.objects.filter(last_index__gt=0, broken=False, enabled=True):
        fetch_source.apply_async(queue=settings.CERTSTREAMS_FETCHING_QUEUE, args=(src.pk,))


@shared_task
def score_all():
    domain_pks = list(models.Domain.objects.filter(score__isnull=True).values_list('pk', flat=True))
    for idx in range(0, len(domain_pks), settings.CERTSTREAMS_SCORING_CHUNK):
        chunk = domain_pks[idx:idx + settings.CERTSTREAMS_SCORING_CHUNK]
        score_domains.apply_async(queue=settings.CERTSTREAMS_SCORING_QUEUE, args=(chunk,))


@shared_task
def cleaning():
    qs = models.Domain.objects.filter(score__lt=settings.CERTSTREAMS_CLEANING_SCORE).order_by('datetime_added')
    pks = qs.values_list('pk', flat=True)[:int(qs.count() * settings.CERTSTREAMS_CLEANING_OLDEST)]
    models.Domain.objects.filter(pk__in=pks).delete()
    models.Domain.objects.update(score=F('score') - settings.CERTSTREAMS_CLEANING_DOWNGRADE)

