"""
Base model classes for the project.
All models should inherit from UUIDModel to use UUID primary keys.
"""
import uuid
from django.db import models


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as primary key.
    All models should inherit from this instead of models.Model.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier (UUID)"
    )
    
    class Meta:
        abstract = True

