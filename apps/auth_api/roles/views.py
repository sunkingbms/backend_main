from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission
from apps.auth_api.accounts.models import CustomUser

from .serializers import (
    PermissionSerializer, 
    RoleSerializer, 
    UserRoleAssignmentSerializer, 
    UserWithRolesSerializer
)

from apps.auth_api.accounts.permissions import IsAdmin

# Create your views here.

class RoleListView(generics.ListCreateAPIView):
    """Create and list roles"""
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    
class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete roles"""
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    
    
class PermissionListView(generics.ListAPIView):
    """List al available permissions"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdmin]
    

@api_view(['POST'])
@permission_classes([IsAdmin])
def assign_user_roles(request, user_id):
    """Assign roles to users"""
    
    try:
        user = CustomUser.objects.get(id=user_id)
        
    except CustomUser.DoesNotExist:
        return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserRoleAssignmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    role_ids = serializer.validated_data['role_ids']
    roles = Group.objects.filter(id__in=role_ids)
    user.groups.set(roles)
    
    return Response(UserWithRolesSerializer(user).data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def user_roles(request, user_id):
    """Get roles for a specific user."""
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(UserWithRolesSerializer(user).data)
    
     
    