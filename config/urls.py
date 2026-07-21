from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .jwt_views import (
    DocumentedTokenBlacklistView,
    DocumentedTokenObtainPairView,
    DocumentedTokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/v1/auth/token/',
         DocumentedTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/',
         DocumentedTokenRefreshView.as_view(),
         name='token_refresh'),
    # POST {"refresh": "..."} — blacklists the refresh token (logout)
    path('api/v1/auth/token/blacklist/',
         DocumentedTokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/listings/', include('listings.urls')),
    path('api/v1/bookings/', include('bookings.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
]
