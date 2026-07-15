import django_filters

from .models import Booking


class BookingFilter(django_filters.FilterSet):

    start_date_from = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['status', 'start_date_from', 'start_date_to']
