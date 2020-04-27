"""Contacts serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Contact

class ContactModelSerializer(serializers.ModelSerializer):
    """Contact model serializer."""

    class Meta:
        """Contact meta class."""

        model = Contact

        fields = (
            'id',
            'company',
            'email',
            'phone',
            'ext_phone'
        )

class CreateContactSerializer(serializers.Serializer):
    """Create company contact."""

    requires_context = True

    phone = serializers.CharField(
        min_length = 6,
        max_length = 15,
        required = False
    )

    ext_phone = serializers.CharField(
        min_length = 1,
        max_length = 5,
        required = False
    )

    email = serializers.CharField(
        min_length = 7,
        max_length = 60,
        required = False
    )

    principal = serializers.BooleanField(required = False)

    def create(self, data):
        """Create new company contacts."""
        company = self.context['company']
        
        contact = Contact.objects.create(
            company = company,
            **data
        )

        return contact