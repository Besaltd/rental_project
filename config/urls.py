from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/token/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/v1/auth/token/blacklist/',
         TokenBlacklistView.as_view(),
         name='token_blacklist'),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/listings/', include('listings.urls')),
    path('api/v1/bookings/', include('bookings.urls')),
    path('api/v1/reviews/', include('reviews.urls')),
]
