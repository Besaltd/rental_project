from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)


@extend_schema(
    summary='Log in',
    description='Login is via email + password (not username), as required by the spec.',
)
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(
    summary='Refresh access token',
    description='Exchanges a valid refresh token for a new access token.',
)
class DocumentedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(
    summary='Log out',
    description=(
        'Blacklists the given refresh token, invalidating it immediately. '
        'The current access token remains valid until it naturally expires.'
    ),
)
class DocumentedTokenBlacklistView(TokenBlacklistView):
    pass
