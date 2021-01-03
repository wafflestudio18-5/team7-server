from django.contrib import admin

from scrap.models import Scrap


class ScrapAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'posting_id']


admin.site.register(Scrap, ScrapAdmin)
