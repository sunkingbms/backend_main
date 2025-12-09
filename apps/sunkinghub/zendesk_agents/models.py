from django.db import models
from django.contrib.auth import get_user_model
from configs.base_models import UUIDModel

User = get_user_model()


class ZendeskProfile(UUIDModel):
    """
    Model to store Zendesk agent profile information.
    Links to Django User model for authentication.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='zendesk_agent',
        help_text="Associated Django user account"
    )
    employee_id = models.CharField(max_length=20, help_text="Agent's company ID number")
    role = models.CharField(max_length=100, null=True, blank=True, default='Agent')
    country = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Agent market"
    )
    username = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Zendesk Agent"
        verbose_name_plural = "Zendesk Agents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Zendesk Agent"

