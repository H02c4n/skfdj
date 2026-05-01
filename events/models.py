from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from parler.models import TranslatableModel, TranslatedFields
from users.models import User
from cloudinary.models import CloudinaryField
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from django.core.exceptions import ValidationError


class RecurrenceRule(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    interval = models.PositiveIntegerField(default=1, help_text=_('Repeat every N days/weeks/months/years'))
    by_day = models.CharField(max_length=50, blank=True, help_text=_('Comma-separated weekdays (MO,TU,WE,TH,FR,SA,SU)'))
    by_month_day = models.PositiveIntegerField(null=True, blank=True, help_text=_('Day of the month (1-31)'))
    end_date = models.DateTimeField(null=True, blank=True, help_text=_('Stop repeating after this date'))
    count = models.PositiveIntegerField(null=True, blank=True, help_text=_('Number of occurrences'))

    class Meta:
        verbose_name = _('Recurrence Rule')
        verbose_name_plural = _('Recurrence Rules')

    def __str__(self):
        return f"{self.get_frequency_display()} / {self.interval}"

    def clean(self):
        if self.frequency == 'weekly' and not self.by_day:
            raise ValidationError(_('Weekly recurrence requires at least one day.'))

    def get_rrule_kwargs(self, dtstart):
        """Return kwargs for dateutil.rrule.rrule based on this rule."""
        freq_map = {'daily': DAILY, 'weekly': WEEKLY, 'monthly': MONTHLY, 'yearly': YEARLY}
        kwargs = {
            'freq': freq_map[self.frequency],
            'interval': self.interval,
            'dtstart': dtstart,
        }
        if self.by_day:
            day_map = {'MO': 0, 'TU': 1, 'WE': 2, 'TH': 3, 'FR': 4, 'SA': 5, 'SU': 6}
            days = [day_map[d.strip()] for d in self.by_day.split(',') if d.strip() in day_map]
            if days:
                kwargs['byweekday'] = days
        if self.by_month_day:
            kwargs['bymonthday'] = self.by_month_day
        if self.count:
            kwargs['count'] = self.count
        if self.end_date:
            kwargs['until'] = self.end_date
        return kwargs

    def generate_occurrences(self, dtstart, from_date=None, to_date=None):
        """Generate datetime occurrences between from_date and to_date."""
        kwargs = self.get_rrule_kwargs(dtstart)
        rule = rrule(**kwargs)
        if from_date and to_date:
            return list(rule.between(from_date, to_date, inc=True))
        elif from_date:
            return list(rule.between(from_date, dtstart.max if not self.end_date else self.end_date, inc=True))
        else:
            return list(rule)


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

    recurrence_rule = models.ForeignKey(
        RecurrenceRule, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='events', verbose_name=_('Recurrence Rule')
    )

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

    def is_full(self, occurrence_date=None):
        if self.capacity is None:
            return False
        if occurrence_date:
            count = self.registrations.filter(occurrence_date=occurrence_date).count()
        else:
            count = self.registrations.count()
        return count >= self.capacity
    
    def get_occurrences(self, from_date, to_date):
        """Return a list of datetime objects for occurrences of this event."""
        if not self.recurrence_rule:
            # Single event – return its date_time if it falls within range
            if from_date <= self.date_time <= to_date:
                return [self.date_time]
            return []
        return self.recurrence_rule.generate_occurrences(self.date_time, from_date, to_date)



class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    occurrence_date = models.DateField(null=True, blank=True, verbose_name=_('Occurrence Date'))


    class Meta:
        unique_together = ('user', 'event', 'occurrence_date')
        verbose_name = _('Event Registration')
        verbose_name_plural = _('Event Registrations')

    def __str__(self):
        occ = f" on {self.occurrence_date}" if self.occurrence_date else ""
        return f"{self.user.email} - {self.event}{occ}"