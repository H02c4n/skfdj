from django.contrib import admin
from django.utils import translation
from parler.admin import TranslatableAdmin
from .models import Event, EventRegistration, RecurrenceRule

@admin.register(RecurrenceRule)
class RecurrenceRuleAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'interval', 'by_day', 'end_date', 'count')
    list_filter = ('frequency',)

@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    def get_queryset(self, request):
        translation.activate("sv")  # 🔥 adminde sv zorla
        return super().get_queryset(request)
    list_display = ('title', 'slug', 'date_time', 'price', 'capacity')
    search_fields = ('translations__title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'image', 'date_time', 'location', 'price', 'capacity')
        }),
        ('Recurrence', {
            'fields': ('recurrence_rule',),
            'description': 'Link to a recurrence rule if this event repeats.'
        }),
    )

    def has_recurrence(self, obj):
        return bool(obj.recurrence_rule)
    has_recurrence.boolean = True
    has_recurrence.short_description = 'Recurring?'



@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'occurrence_date')
    list_filter = ('event',)
    search_fields = ('user__email', 'event__translations__title')
    readonly_fields = ('occurrence_date',)