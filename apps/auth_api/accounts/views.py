import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_spectacular.utils import extend_schema

from google.auth.exceptions import TransportError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .permissions import IsAdmin, IsOwnerOrAdmin
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    UserDetailSerializer, 
    GoogleTokenSerializer, 
    GoogleAutoResponseSerializer, 
    LogoutSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """
    Register a new user account.
    
    Creates a new user with email, password, first name, and last name.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserSerializer, 400: 'Bad Request'},
        description='Register a new user account',
        summary='Register user'
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
class MeView(APIView):
    """ GET /api/me/ - used to return logged in user detail """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response(UserSerializer(request.user).data)
    
class UserListView(generics.ListAPIView):
    """List all user (admin only)"""
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdmin]
    
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user"""
    queryset = CustomUser.objects.all()
    permission_classes = [IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return UserDetailSerializer
        return UserSerializer
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=LogoutSerializer,
        responses={205: None, 400: 'Invalid token'},
        description='Login a user out',
        summary='User Logout'
    )
    
    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh_token"]
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    
class GoogleLoginView(APIView):
    """ 
    POST /api/google/login/
    Body: {"id_token":"key"}
    verify google id token
    create or get a user
    return a simple jwt refresh_token/access_token/user
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=GoogleTokenSerializer,
        responses={200: GoogleAutoResponseSerializer, 400: 'Bad Request', 403: 'Forbidden'},
        description='Authenticate using Google ID token',
        summary='Google login'
    )
    def post(self, request):
        token_serializer = GoogleTokenSerializer(data=request.data)
        token_serializer.is_valid(raise_exception=True)
        id_token_str = token_serializer.validated_data["id_token"]
        
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response({"detail": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
        except TransportError:
            logger.exception("Unable to reach Google to verify ID token")
            return Response({"detail": "Unable to verify Google token"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        email = id_info.get("email")
        first_name = id_info.get("given_name")
        last_name = id_info.get("family_name")
        email_verified = id_info.get("email_verified")
        issuer = id_info.get("iss")

        if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
            return Response({"detail": "Invalid Google token issuer"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response(
                {"detail": "Google token does not contain email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email_verified:
            return Response(
                {"detail": "Google account email is not verified"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"first_name": first_name or "", "last_name": last_name or "", "is_active": True}
        )
        if not user.is_active:
            return Response({"detail": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN)
        # Generate JWT Token
        refresh = RefreshToken.for_user(user)
        auth_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        }
        
        response_serializer = GoogleAutoResponseSerializer(auth_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)