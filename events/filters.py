import django_filters
from django.db.models import Q
from .models import Event


class EventFilter(django_filters.FilterSet):
    date_time__gte = django_filters.DateTimeFilter(field_name='date_time', lookup_expr='gte')
    date_time__lte = django_filters.DateTimeFilter(field_name='date_time', lookup_expr='lte')

    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')

    # Handle exact price query (e.g., price=0 or price=245)
    price = django_filters.NumberFilter(method='filter_price_exact')

    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Event
        fields = [
            'date_time__gte',
            'date_time__lte',
            'price__gte',
            'price__lte',
            'price__gt',
            'price',
        ]
    
    def filter_price_exact(self, queryset, name, value):
        """
        If value == 0, include events with price=0 OR price__isnull=True (free events).
        Otherwise, filter by exact price.
        """
        if value == 0:
            # Free: price = 0 or price is NULL
            return queryset.filter(Q(price=0) | Q(price__isnull=True))
        return queryset.filter(price=value)

    def filter_search(self, queryset, name, value):
        language = getattr(self.request, 'LANGUAGE_CODE', 'sv')

        return queryset.filter(
            Q(translations__language_code=language) &
            (
                Q(translations__title__icontains=value) |
                Q(translations__description__icontains=value) |
                Q(translations__location__icontains=value)
            )
        ).distinct()