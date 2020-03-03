from django.db.models import F
from django.contrib import admin

from certstreams import models


class DomainAdmin(admin.ModelAdmin):

    list_display = ('name_filtered', 'name_original', 'score', 'datetime_added')
    ordering = (F('score').desc(nulls_last=True),)
    search_fields = ('name_filtered', 'name_original',)


admin.site.register(models.Source)
admin.site.register(models.Domain, DomainAdmin)
admin.site.register(models.Keyword)
admin.site.register(models.TLD)
