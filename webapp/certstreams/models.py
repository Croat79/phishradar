from django.db import models

from certstreams import generators


class Source(models.Model):

    url = models.URLField(unique=True)
    last_index = models.BigIntegerField(default=0)
    broken = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.url


class Issuer(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Domain(models.Model):

    source = models.ForeignKey('certstreams.Source', on_delete=models.CASCADE)
    issuer = models.ForeignKey('certstreams.Issuer', on_delete=models.CASCADE)
    name_filtered = models.CharField(max_length=255)
    name_original = models.CharField(max_length=255)
    fingerprint = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    datetime_added = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)
    score = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name_filtered


class Keyword(models.Model):

    name = models.CharField(max_length=255, unique=True)
    partial = models.BooleanField(default=False)
    original = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        generate_hgos = not(bool(self.pk))
        super().save(*args, **kwargs)
        if generate_hgos:
            hgos = generators.generate_homoglyphs(self.name)
            hgos.remove(self.name)
            objs = [Keyword(original_id=self.pk, name=hgo) for hgo in hgos]
            Keyword.objects.bulk_create(objs)


class TLD(models.Model):

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
