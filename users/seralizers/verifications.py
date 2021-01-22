# Serializers verifications

# Django
from django.conf import settings

# Django REST Framework
from rest_framework import serializers

# JWT
import jwt


# User verification payload type
USER_VERIFICATION_PAYLOAD_TYPE = 'user_email_confirmation'


def generate_user_verification_token(user):
    """Create JWT token that the user can use to verify its account."""
    payload = {
        'user': user.username,
        'type': USER_VERIFICATION_PAYLOAD_TYPE
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')
    return token.decode()


def validate_user_verification_token(token):
    """Recieves the verification JWT token of a company, 
    validate if its correct and returns the payload."""

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = 'HS256')
    except jwt.ExpiredSignatureError:
        raise serializers.ValidationError('Verification link has expired')
    except jwt.PyJWTError:
        raise serializers.ValidationError('Invalid token')

    if payload['type'] != USER_VERIFICATION_PAYLOAD_TYPE:
        raise serializers.ValidationError('Invalid token')

    return payload


# Here comes the serializers for automatic email notification