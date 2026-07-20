from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics, permissions, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Register',
        description=(
            'Creates a new account. role is fixed at registration and '
            'cannot be changed later via the API.'
        ),
        examples=[
            OpenApiExample(
                'Landlord registration',
                value={
                    'username': 'jane_landlord',
                    'email': 'jane@example.com',
                    'password': 'StrongPass123',
                    'password2': 'StrongPass123',
                    'role': 'landlord',
                    'phone': '+491234567890',
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileView(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  generics.GenericAPIView,):

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(tags=['Auth'], summary='Get own profile')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(tags=['Auth'], summary='Edit own profile', description='role is read-only here')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Change password',
        description=(
            'Requires the current password. On success, all outstanding '
            'refresh tokens for this user are blacklisted immediately — '
            'the current access token stays valid until it naturally '
            'expires (up to 60 minutes), since individual access tokens '
            'cannot be revoked.'
        ),
        request=ChangePasswordSerializer,
        responses={200: None},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'The password has been successfully changed'})
