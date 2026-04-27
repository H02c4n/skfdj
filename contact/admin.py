from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    actions = ['mark_processed']

    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_processed.short_description = "Mark selected messages as processed"