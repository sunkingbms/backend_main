from rest_framework import serializers
from .models import ZendeskProfile



class ZendeskProfileSerializer(serializers.ModelSerializer):
    """Serializer for Zendesk Agent profile"""
    class Meta:
        model = ZendeskProfile
        fields = [
            'employee_id',
            'role',
            'country',
            'created_at'
        ]

