import django_filters
from django.utils import timezone

from .models import Booking


class BookingFilter(django_filters.FilterSet):

    start_date_from = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte')
    is_completed = django_filters.BooleanFilter(method='filter_is_completed')

    class Meta:
        model = Booking
        fields = ['status', 'start_date_from', 'start_date_to', 'is_completed']

    def filter_is_completed(self, queryset, name, value):
        today = timezone.localdate()
        completed = {'status': Booking.Status.CONFIRMED, 'end_date__lt': today}
        if value:
            return queryset.filter(**completed)
        return queryset.exclude(**completed)
