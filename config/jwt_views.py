from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)


@extend_schema(
    tags=['Auth'],
    summary='Log in',
    description='Login is via email + password (not username), as required by the spec.',
    examples=[
        OpenApiExample(
            'Login request',
            value={'email': 'jane@example.com', 'password': 'StrongPass123'},
            request_only=True,
        ),
    ],
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    tags=['Auth'],
    summary='Refresh access token',
    description='Exchanges a valid refresh token for a new access token.',
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=['Auth'],
    summary='Log out',
    description=(
        'Blacklists the given refresh token, invalidating it immediately. '
        'The current access token remains valid until it naturally expires.'
    ),
)
class DocumentedTokenBlacklistView(TokenBlacklistView):
    pass
