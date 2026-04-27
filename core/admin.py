from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from .models import SiteSettings, BoardMember
from django.utils.translation import gettext_lazy as _



@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslatableAdmin):
    fieldsets = (
        (_('Organization'), {
            'fields': (
                'organization_name',
                'org_number',
                'logo',
                'founded_year',
                'hero_background',
            )
        }),
        (_('Contact'), {
            'fields': (
                'email',
                'phone',
                'address',
                'website',
            )
        }),
        (_('Social Media'), {
            'fields': (
                'facebook',
                'instagram',
                'linkedin',
            )
        }),
        # ✅ Translatable field'ları buraya ekle
        (_('Content'), {
            'fields': (
                'mission',
                'vision',
                'short_description',
            )
        }),
    )

@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'email', 'order', 'image_preview')
    list_editable = ('order',)
    fields = ('name', 'title', 'email', 'image', 'order')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = _('Photo')