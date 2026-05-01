from django.urls import path
from .views import EventListView, EventDetailView, EventRegistrationView, EventCalendarView, UpcomingEventsView

app_name = 'events'

urlpatterns = [
    path('events/calendar/', EventCalendarView.as_view(), name='event-calendar'),
    path('events/upcoming/', UpcomingEventsView.as_view(), name='event-upcoming'),
    path('events/', EventListView.as_view(), name='event-list'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('events/<slug:slug>/register/', EventRegistrationView.as_view(), name='event-register'),
    
]