from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from apps.sunkinghub.zendesk_agents.serializers import ZendeskProfileSerializer


User = get_user_model() 

class GoogleTokenSerializer(serializers.Serializer):
    """Serializer for Google ID token verification request"""
    id_token = serializers.CharField(required=True, help_text="Google ID token from frontend")

class UserRegistrationSerializer(serializers.ModelSerializer):
    """ Serializer used for register users """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        help_text="User password. Must meet Django password validation requirements."
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        help_text="Confirm password. Must match the password field."
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'help_text': 'User email address. Must be unique.'},
            'first_name': {'required': True, 'help_text': 'User first name'},
            'last_name': {'required': True, 'help_text': 'User last name'},
        }
        
    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': ['Passwords did not match']})
        
        return attrs
    
    def create(self, validated_data: dict) -> User:
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data in response"""
    zendesk_profile = ZendeskProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'zendesk_profile']
        read_only_fields = fields
        
        
class UserDetailSerializer(UserSerializer):
    """Extended user serializer for detailed views (admin)"""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['is_staff', 'is_superuser']
        
    
class GoogleAutoResponseSerializer(serializers.Serializer):
    """Serializer for Google auth response"""
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    user = UserSerializer(help_text="User information")
    
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

