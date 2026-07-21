import django_filters

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    """
    Filters for GET /api/v1/listings/?...

    Example query params:
    ?price_min=300&price_max=800
    ?rooms_min=2&rooms_max=4
    ?city=Hildesheim
    ?property_type=apartment
    ?search=cozy+studio       (searches title and description, separate SearchFilter)
    ?ordering=price           (ascending)
    ?ordering=-price          (descending)
    ?ordering=-created_at     (newest first, this is also the default)
    """

    price_min = django_filters.NumberFilter(
        field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(
        field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(
        field_name='rooms', lookup_expr='lte')
    city = django_filters.CharFilter(
        field_name='city', lookup_expr='icontains')
    property_type = django_filters.ChoiceFilter(
        choices=Listing.PropertyType.choices)

    class Meta:
        model = Listing
        fields = ['price_min', 'price_max', 'rooms_min',
                  'rooms_max', 'city', 'property_type']
