from django.contrib import admin
from django.utils import translation
from parler.admin import TranslatableAdmin
from .models import Event, EventRegistration

@admin.register(Event)
class EventAdmin(TranslatableAdmin):
    def get_queryset(self, request):
        translation.activate("sv")  # 🔥 adminde sv zorla
        return super().get_queryset(request)
    list_display = ('title', 'slug', 'date_time', 'price', 'capacity')
    search_fields = ('translations__title',)

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at')
    list_filter = ('event',)
    search_fields = ('user__email', 'event__translations__title')