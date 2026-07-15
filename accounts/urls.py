from django.urls import path
from .views import ProfileView, RegisterView, ChangePasswordView


app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
