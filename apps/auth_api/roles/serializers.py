from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from apps.auth_api.accounts.models import CustomUser


class PermissionSerializer(serializers.ModelSerializer):
    """Handling Permissions serialization"""
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']
        
class RoleSerializer(serializers.ModelSerializer):
    """Serializer for user roles (Django Group)"""
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_list = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permissions_list']
        
    def create(self, validated_data):
        permissions_ids = validated_data.pop('permissions_list', [])
        group = Group.objects.create(**validated_data)
        
        if permissions_ids:
            permissions = Permission.objects.filter(id__in=permissions_ids)
            group.permissions.set(permissions)
        
        return group
    
    def update(self, instance, validated_data):
        permissions_ids = validated_data.pop('permissions_list', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        
        if permissions_ids is not None:
            permissions = Permission.objects.filter(id__in=permissions_ids)
            instance.permissions.set(permissions)
            
        return instance
    
class UserRoleAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning roles to user"""
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

class UserWithRolesSerializer(serializers.ModelSerializer):
    """User serializer with role information"""
    roles=RoleSerializer(source='groups', many=True, read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'roles']