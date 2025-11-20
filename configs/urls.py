"""
URL configuration for configs project.
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.auth_api.accounts.views import RegisterView, MeView, GoogleLoginView, LogoutView
from apps.sunkinghub.zendesk_agents.views import LinkZendeskUserView, ZendeskProfileListView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # The below link is the online documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    #Auth
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='auth_token'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    
    #Google Auth
    path('api/auth/google/login/', GoogleLoginView.as_view(), name='google_login'),
    
    # Users
    path('api/', include('apps.auth_api.accounts.urls')),
    
    # Zendesk Link
    path('api/zendesk/link/', LinkZendeskUserView.as_view(), name='zendesk_link'),
    path("api/zendesk/profiles/", ZendeskProfileListView.as_view(), name="zendesk-profiles"),
    
    # Roles
    path('api/', include('apps.auth_api.roles.urls')),
]
