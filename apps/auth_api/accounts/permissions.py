from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access to admin only"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owner or admin"""
    
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj == request.user
        
        