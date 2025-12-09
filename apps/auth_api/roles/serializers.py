from rest_framework import serializers
from django.contrib.auth.models import Permission
from apps.auth_api.accounts.models import CustomUser
from .models import Role, RolePermission, UserRole


class PermissionSerializer(serializers.ModelSerializer):
    """Handling Permissions serialization"""

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']


class SimpleRoleSerializer(serializers.ModelSerializer):
    """Lightweight role representation"""

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'category', 'is_active']
        read_only_fields = fields


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for custom Role model"""

    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of permission IDs to attach to the role",
    )
    permission_scope = serializers.CharField(
        write_only=True,
        required=False,
        default="global",
        help_text="Scope applied to all provided permissions",
    )
    permission_can_grant = serializers.BooleanField(
        write_only=True,
        required=False,
        default=True,
        help_text="Whether this role can grant the attached permissions",
    )

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'code',
            'description',
            'category',
            'is_active',
            'permissions',
            'permission_ids',
            'permission_scope',
            'permission_can_grant',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'permissions', 'created_at', 'updated_at']

    def _sync_permissions(self, role, permission_ids, scope, can_grant):
        role.rolepermission_set.all().delete()
        if not permission_ids:
            return
        perms = Permission.objects.filter(id__in=permission_ids)
        RolePermission.objects.bulk_create(
            [
                RolePermission(
                    role=role,
                    permission=perm,
                    scope=scope,
                    can_grant=can_grant,
                )
                for perm in perms
            ]
        )

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        scope = validated_data.pop('permission_scope', 'global')
        can_grant = validated_data.pop('permission_can_grant', True)
        role = Role.objects.create(**validated_data)
        self._sync_permissions(role, permission_ids, scope, can_grant)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        scope = validated_data.pop('permission_scope', 'global')
        can_grant = validated_data.pop('permission_can_grant', True)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if permission_ids is not None:
            self._sync_permissions(instance, permission_ids, scope, can_grant)
        return instance


class UserRoleAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning roles to user"""

    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="List of role IDs to set for the user",
    )


class UserRoleSerializer(serializers.ModelSerializer):
    """User role link with role details"""

    role = SimpleRoleSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ['role', 'expires_at', 'is_active', 'assigned_at', 'assigned_by', 'notes']
        read_only_fields = ['assigned_at', 'assigned_by']


class UserWithRolesSerializer(serializers.ModelSerializer):
    """User serializer with role information"""

    roles = UserRoleSerializer(source='user_roles', many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'roles']