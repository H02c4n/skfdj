from django.db import models
from django.utils.translation import gettext_lazy as _

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"