from django.db import IntegrityError
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, OpenApiExample
from rest_framework import permissions as drf_permissions
from rest_framework import viewsets, serializers

from .models import Review
from .permissions import IsReviewAuthorOrReadOnly
from .serializers import ReviewCreateSerializer, ReviewSerializer, ReviewUpdateSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Reviews'],
        summary='List reviews',
        description=(
            'Public list of reviews. Use ?listing={id} to see reviews '
            'for one specific listing — without it, all reviews across '
            'the platform are returned.'
        ),
        parameters=[
            OpenApiParameter(
                name='listing',
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter reviews by listing id.',
            ),
        ],
    ),
    create=extend_schema(
        tags=['Reviews'],
        summary='Leave a review',
        description=(
            'Only allowed for the tenant of a CONFIRMED booking whose '
            'stay is already over (end_date has passed), and only once '
            'per booking. See User.can_review for the exact rules.'
        ),
        examples=[
            OpenApiExample(
                'Positive review',
                value={'booking': 1, 'rating': 5,
                       'comment': 'Great place, would stay again!'},
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=['Reviews'],
        summary='Edit own review',
        description='Only rating and comment can be changed; author only.',
    ),
    destroy=extend_schema(
        tags=['Reviews'], summary='Delete own review', description='Author only.',
    ),
    retrieve=extend_schema(
        tags=['Reviews'], summary='Review detail', description='Public.'),
)
class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = Review.objects.select_related('listing', 'author')
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [drf_permissions.IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [drf_permissions.IsAuthenticated(), IsReviewAuthorOrReadOnly()]
        return [drf_permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            raise serializers.ValidationError(
                {'booking': 'A review for this reservation already exists.'}
            )

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        serializer.save(author=self.request.user, listing=booking.listing)
