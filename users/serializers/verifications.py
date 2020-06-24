"""Verifications serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from users.models import User, Verification

# Serializers
from multimedia.serializers.documents import DocumentModelSerializer

class VerificationModelSerializer(serializers.ModelSerializer):
    """Verification model serializer."""

    documents = DocumentModelSerializer(many = True)

    class Meta:
        """Verification meta class."""

        model = Verification

        fields = (
            'id',
            'state',
            'verified',
            'documents',
            'application_date',
            'finish_date',
        )

        read_only_fields = (
            'verified',
            'state',
            'application_date',
            'finish_date'
        )