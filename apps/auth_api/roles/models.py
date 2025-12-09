from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.conf import settings
from configs.base_models import UUIDModel

class Role(UUIDModel):
    """
    Role model for Role-Based Access Control
    """
  
    name = models.CharField(_('role name'), max_length=100, unique=True)
    code = models.SlugField(_('role code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    category = models.CharField(
        _('category'),
        max_length=20
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
        related_name='roles',
        through='RolePermission'
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def has_permission(self, permission_codename):
        """Check if role has specific permission"""
        return self.permissions.filter(codename=permission_codename).exists()

class RolePermission(UUIDModel):
    """
    Junction table for Role-Permission with additional context
    """
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    scope = models.CharField(
        _('scope'),
        max_length=20,
        blank=True,
        default='global'
    )
    can_grant = models.BooleanField(
        _('can grant'),
        default=True,
        help_text="Can users with this role grant this permission to others?"
    )
    
    granted_at = models.DateTimeField(_('granted at'), auto_now_add=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions'
    )
    
    class Meta:
        verbose_name = _('role permission')
        verbose_name_plural = _('role permissions')
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

class UserRole(UUIDModel):
    """
    User-Role assignment with context
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    
    notes = models.TextField(_('notes'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
