"""Verifications serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from users.models import User, Verification

class VerificationModelSerializer(serializers.ModelSerializer):
    """Verification model serializer."""

    class Meta:
        """Verification meta class."""

        model = Verification

        fields = (
            'id',
            'verified',
            'state',
            'application_date',
            'finish_date'
        )

        read_only_fields = (
            'verified',
            'state',
            'application_date',
            'finish_date'
        )