from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import UserSerializer, UserTokenSerializer


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserTokenAPIView(ObtainAuthToken):
    serializer_class = UserTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_object(self):
        return self.request.user
