import django_filters
from django.utils import timezone

from .models import Booking


class BookingFilter(django_filters.FilterSet):
    """
    Filters for GET /api/v1/bookings/?...

    ?status=pending                 (one of the statuses)
    ?start_date_from=2026-08-01     (bookings with a start date not earlier than)
    ?start_date_to=2026-08-31       (not later than)
    ?is_completed=true              (CONFIRMED, and end_date has already passed)
    ?is_completed=false             (everything else — active/pending/cancelled)
    """
    start_date_from = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte')
    is_completed = django_filters.BooleanFilter(method='filter_is_completed')

    class Meta:
        model = Booking
        fields = ['status', 'start_date_from', 'start_date_to', 'is_completed']

    def filter_is_completed(self, queryset, name, value):
        # "Completed" is not stored as a separate status in the DB —
        # it's a derived flag: the booking is confirmed, and the
        # end date has already passed
        today = timezone.localdate()
        completed = {'status': Booking.Status.CONFIRMED, 'end_date__lt': today}
        if value:
            return queryset.filter(**completed)
        return queryset.exclude(**completed)
