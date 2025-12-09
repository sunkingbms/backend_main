import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from .managers import CustomUserManager
from configs.base_models import UUIDModel

class CustomUser(UUIDModel, AbstractBaseUser, PermissionsMixin):
    '''Custom user '''
    # Required Fields
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal Information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    country = models.CharField(_('country'), max_length=20)
    
    # Company Information
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # User Status
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)
    
    # Timestamps
    last_updated = models.DateTimeField(_('last updated'), auto_now=True)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    
    # Social Login
    google_id = models.CharField(_('Google ID'), max_length=255, blank=True, null=True)
    
    # Security
    password_changed_at = models.DateTimeField(_('password changed at'), blank=True, null=True)
    failed_login_attempts = models.IntegerField(_('failed login attempts'), default=0)
    account_locked_until = models.DateTimeField(_('account locked until'), blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'employee_id', 'country']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_account_locked(self):
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, minutes=15):
        """Lock account for specified minutes"""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
        
class AuditLog(models.Model):
    """
    Audit logging for authentication events
    """
    EVENT_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    event_type = models.CharField(_('event type'), max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    user_agent = models.TextField(_('user agent'), blank=True, null=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email if self.user else 'Unknown'} - {self.event_type}"