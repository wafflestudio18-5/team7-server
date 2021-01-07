from django.contrib import admin

from subscription.models import Subscription


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'subscriber_id', 'writer_id']


admin.site.register(Subscription, SubscriptionAdmin)
