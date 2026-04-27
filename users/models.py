from datetime import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('member', _('Member')),
        ('volunteer', _('Volunteer')),
        ('admin', _('Admin')),
    )
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_volunteer = models.BooleanField(
        default=False,
        help_text=_('Designates whether the user has been approved as a volunteer.')
    )
    bio = models.TextField(blank=True, verbose_name=_('Biography'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone number'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class MembershipCancellationRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Surec devam ediyor')),
        ('approved', _('Onaylandi')),
        ('rejected', _('Reddedildi')),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cancellation_requests',
        verbose_name=_('User')
    )
    reason = models.TextField(verbose_name=_('Reason for cancellation'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Reviewed at'))
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_cancellations',
        verbose_name=_('Reviewed by')
    )

    class Meta:
        verbose_name = _('Membership Cancellation Request')
        verbose_name_plural = _('Membership Cancellation Requests')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='pending'),
                name='unique_pending_cancellation_per_user'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"

    def approve(self, reviewed_by):
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by
        self.save()
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

    def reject(self, reviewed_by):
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.reviewed_by = reviewed_by
        self.save()