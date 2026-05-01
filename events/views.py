from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Event, EventRegistration
from .serializers import EventListSerializer, EventOccurrenceSerializer, EventDetailSerializer, EventRegistrationSerializer, CalendarEventSerializer, EventMiniSerializer
from .permissions import IsAdminOrReadOnly
from collections import defaultdict
from django.utils import timezone
from .filters import EventFilter
from .recurrence import expand_events
from datetime import datetime, time



class EventListView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('date_time')
    serializer_class = EventListSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['translations__title', 'translations__description']
    ordering_fields = ['date_time', 'price', 'created_at']

class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    lookup_field = 'slug'

class EventRegistrationView(generics.CreateAPIView):
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        event_slug = self.kwargs.get('slug')
        try:
            event = Event.objects.get(slug=event_slug)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        occurrence_date = request.data.get('occurrence_date')
        if event.recurrence_rule and not occurrence_date:
            return Response(
                {"detail": "occurrence_date is required for recurring events."},
                status=status.HTTP_400_BAD_REQUEST
            )

        occ_date = None
        if occurrence_date:
            try:
                occ_date = datetime.strptime(occurrence_date, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Validate occurrence if event is recurring
            if event.recurrence_rule:
                occ_datetime_start = timezone.make_aware(datetime.combine(occ_date, time.min))
                occ_datetime_end = timezone.make_aware(datetime.combine(occ_date, time.max))
                valid_dates = [d.date() for d in event.get_occurrences(occ_datetime_start, occ_datetime_end)]
                
                if occ_date not in valid_dates:
                    return Response(
                        {"detail": "Not a valid occurrence date for this event."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Capacity check (supports occurrence‑specific capacity)
        if event.is_full(occurrence_date=occ_date):
            return Response({"detail": "Event is full."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicate registration for the same occurrence
        filter_kwargs = {'user': request.user, 'event': event}
        if occ_date:
            filter_kwargs['occurrence_date'] = occ_date
        if EventRegistration.objects.filter(**filter_kwargs).exists():
            return Response(
                {"detail": "You are already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = EventRegistration.objects.create(
            user=request.user,
            event=event,
            occurrence_date=occ_date
        )
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class EventCalendarView(APIView):
    """
    Returns events grouped by date, expanding recurrences.
    Optional query param: ?month=YYYY-MM
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        month_param = request.query_params.get('month')
        now = timezone.now()

        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                from_date = timezone.make_aware(datetime(year, month, 1))
                if month == 12:
                    to_date = timezone.make_aware(datetime(year+1, 1, 1)) - timezone.timedelta(seconds=1)
                else:
                    to_date = timezone.make_aware(datetime(year, month+1, 1)) - timezone.timedelta(seconds=1)
            except (ValueError, TypeError):
                return Response({"detail": "Invalid month format. Use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            from_date = now
            to_date = now + timezone.timedelta(days=30)

        # Prefetch all needed data
        events = Event.objects.prefetch_related('translations', 'recurrence_rule')
        occurrences = list(expand_events(events, from_date, to_date))

        # Group by date
        grouped = defaultdict(list)
        for occ in occurrences:
            date_key = occ['date_time'].date().isoformat()
            grouped[date_key].append(occ)

        result = []
        for date_str in sorted(grouped.keys()):
            result.append({
                'date': date_str,
                'events': grouped[date_str]
            })

        return Response(result)


class UpcomingEventsView(APIView):
    """
    GET /api/events/upcoming/
    Returns future occurrences (including recurrences), limited to 10.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        now = timezone.now()
        soon = now + timezone.timedelta(days=30)  # next 30 days
        events = Event.objects.prefetch_related('translations', 'recurrence_rule')
        occurrences = list(expand_events(events, now, soon))
        occurrences.sort(key=lambda x: x['date_time'])
        serializer = EventOccurrenceSerializer(occurrences[:10], many=True)
        return Response(serializer.data)