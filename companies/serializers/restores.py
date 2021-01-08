"""Restores serializers."""

# Django
from django.contrib.auth import password_validation

# DRF
from rest_framework import serializers

class RestorePasswordSerializer(serializers.Serializer):

    new_password = serializers.CharField(min_length=8, max_length=64)
    new_password_confirmation = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Validate that new passwords match"""
        new_password = data['new_password']
        new_password_conf = data['new_password_confirmation']

        if new_password != new_password_conf:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        password_validation.validate_password( new_password )
        
        return data