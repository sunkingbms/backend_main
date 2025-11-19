from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager

from configs.base_models import UUIDModel

# Create your models here.

# Custom user class inheriting from the base user class and extending the user fields
class CustomUser(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """
    Custom user model for the entire application, using only email as the unique identifier
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        
    def __str__(self) -> str:
        """ Default method returned when CustomUser model is called """
        return self.email
    
    def get_full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
