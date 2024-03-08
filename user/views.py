from django.shortcuts import render

# Create your views here.
"""
Views for the user API.
"""

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.views import APIView


from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)

    
class CreateUserView(generics.CreateAPIView):
        """Create a new user in the system."""
        serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES




class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated User."""
        return self.request.user
    

class LogoutView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Déconnexion de l'utilisateur
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)    