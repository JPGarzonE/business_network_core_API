# Serializers users

# Django REST Framework
from rest_framework import serializers

# Models
from ..models import User


class UserModelSerializer(serializers.ModelSerializer):
    """Serializer that represents a user."""

    class Meta:
        model = User

        fields = (
            'id', 
            'username', 
            'email', 
            'full_name', 
            'is_verified', 
            'is_staff',
        )