from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from parler.models import TranslatableModel, TranslatedFields
from users.models import User
from cloudinary.models import CloudinaryField
class Event(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name=_('Title')),
        description=models.TextField(verbose_name=_('Description')),
        location=models.CharField(max_length=255, verbose_name=_('Location')),
    )
    slug = models.SlugField(unique=True, blank=True)  # Allow blank, auto-generate
    
    #image = models.ImageField(upload_to='events/', verbose_name=_('Image'))
    image = CloudinaryField('events', blank=True, null=True)

    date_time = models.DateTimeField(verbose_name=_('Date and time'))
    capacity = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1)],
        verbose_name=_('Capacity')
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True, default=0,
        verbose_name=_('Price (SEK)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['date_time']

    def __str__(self):
        return self.safe_translation_getter('title', self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Use the title from the default language (first in PARLER_LANGUAGES)
            title = self.safe_translation_getter('title', any_language=True)
            if title:
                self.slug = slugify(title)
            else:
                self.slug = f"event-{self.date_time.strftime('%Y%m%d')}"
        super().save(*args, **kwargs)

    def is_free(self):
        return self.price is None or self.price == 0

    def available_spots(self):
        if self.capacity is None:
            return None
        return self.capacity - self.registrations.count()

    def is_full(self):
        if self.capacity is None:
            return False
        return self.registrations.count() >= self.capacity

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')
        verbose_name = _('Event Registration')
        verbose_name_plural = _('Event Registrations')

    def __str__(self):
        return f"{self.user.email} - {self.event}"