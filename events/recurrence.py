from datetime import datetime, time
from django.utils import timezone
from .models import Event

def expand_events(queryset, from_date, to_date):
    """
    Given a queryset of events (with recurrence_rule prefetched),
    yield all occurrences as dicts with full event data.
    """
    for event in queryset:
        if event.recurrence_rule:
            dates = event.get_occurrences(from_date, to_date)
        else:
            if from_date <= event.date_time <= to_date:
                dates = [event.date_time]
            else:
                dates = []

        for dt in dates:
            # Build a lightweight serialisable object
            yield {
                'id': event.id,
                'title': event.safe_translation_getter('title', default=''),
                'slug': event.slug,
                'date_time': dt,
                'time': dt.strftime('%H:%M'),
                'price': event.price,          # full price info later
                'is_free': event.is_free(),
                'attendees_count': event.registrations.filter(occurrence_date=dt.date()).count(),
                'capacity': event.capacity,
                'image': event.image.url if event.image else None,
                'location': event.safe_translation_getter('location', default=''),
                'occurrence_date': dt.date().isoformat(),
            }