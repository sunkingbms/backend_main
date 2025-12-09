import uuid
from rest_framework import serializers
from .models import ZendeskProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class MinimalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name")
        read_only_fields = fields

class ZendeskProfileSerializer(serializers.ModelSerializer):
    """Serializer for Zendesk Agent profile"""
    user = MinimalUserSerializer(read_only=True)
    user_id = serializers.UUIDField(
        write_only=True,
        required=False,
        help_text='Id of user to link'
    )
    class Meta:
        model = ZendeskProfile
        fields = ("id", "user", "user_id", "employee_id", "role", "country", "username", "created_at")
        read_only_fields = ('id', 'user', 'created_at')
        
        
    def _resolve_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User with the id does not exist"})
    
    def create(self, validated_data):
        user_id = validated_data.pop("user_id", None)
        if user_id:
            user = self._resolve_user(user_id)
        else:
            request = self.context.get("request")
            if request and not request.user.is_anonymous:
                user = request.user
            else:
                raise serializers.ValidationError({"user_id": "user_id is required when request user is anonymous."})

        profile = ZendeskProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_id = validated_data.pop("user_id", None)
        if user_id:
            instance.user = self._resolve_user(user_id)

        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
