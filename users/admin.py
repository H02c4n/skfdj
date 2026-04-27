from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MembershipCancellationRequest
from django.utils.translation import gettext_lazy as _

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_volunteer', 'is_staff')
    list_filter = ('role', 'is_volunteer', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        (_('Additional Info'), {'fields': ('role', 'is_volunteer', 'bio', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Additional Info'), {'fields': ('role', 'is_volunteer', 'bio', 'phone')}),
    )

@admin.register(MembershipCancellationRequest)
class MembershipCancellationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'reason')
    readonly_fields = ('created_at', 'reviewed_at', 'reviewed_by')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.approve(request.user)
        self.message_user(request, _('Selected requests have been approved.'))
    approve_requests.short_description = _('Approve selected cancellation requests')

    def reject_requests(self, request, queryset):
        for req in queryset.filter(status='pending'):
            req.reject(request.user)
        self.message_user(request, _('Selected requests have been rejected.'))
    reject_requests.short_description = _('Reject selected cancellation requests')