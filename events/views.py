from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Event, EventRegistration
from .serializers import EventListSerializer, EventDetailSerializer, EventRegistrationSerializer, CalendarEventSerializer, EventMiniSerializer
from .permissions import IsAdminOrReadOnly
from collections import defaultdict
from django.utils import timezone
from .filters import EventFilter


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

        if event.is_full():
            return Response({"detail": "Event is full."}, status=status.HTTP_400_BAD_REQUEST)

        if EventRegistration.objects.filter(user=request.user, event=event).exists():
            return Response({"detail": "You are already registered."}, status=status.HTTP_400_BAD_REQUEST)

        registration = EventRegistration.objects.create(user=request.user, event=event)
        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class EventCalendarView(APIView):
    """
    Returns events grouped by date.
    Optional query param: ?month=YYYY-MM
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Base queryset with translations prefetched
        queryset = Event.objects.all().prefetch_related('translations')

        # Optional month filter
        month_param = request.query_params.get('month')
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                queryset = queryset.filter(
                    date_time__year=year,
                    date_time__month=month
                )
            except (ValueError, TypeError):
                pass

        # Order by date_time ascending
        queryset = queryset.order_by('date_time')

        # Group by date
        grouped = defaultdict(list)
        for event in queryset:
            date_key = event.date_time.date().isoformat()
            grouped[date_key].append(event)

        # Serialize
        result = []
        for date_str in sorted(grouped.keys()):
            events_data = CalendarEventSerializer(grouped[date_str], many=True).data
            result.append({
                'date': date_str,
                'events': events_data
            })

        return Response(result)
    

class UpcomingEventsView(generics.ListAPIView):
    """
    GET /api/events/upcoming/
    Returns future events, ordered by date ascending, limited to 10.
    """
    serializer_class = EventMiniSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(date_time__gte=now).prefetch_related('translations').order_by('date_time')[:10]