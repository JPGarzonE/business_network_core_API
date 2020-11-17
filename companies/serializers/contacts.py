"""Contacts serializer."""

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

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
            'area_code',
            'phone',
        )

class HandleCompanyContactSerializer(serializers.ModelSerializer):
    """Create and update company contact."""

    requires_context = True

    area_code = serializers.CharField(
        min_length = 1,
        max_length = 5,
        required = False,
        allow_null = True
    )

    phone = serializers.CharField(
        min_length = 6,
        max_length = 15,
        required = False,
        allow_null = True
    )

    email = serializers.CharField(
        min_length = 7,
        max_length = 60,
        required = False,
        allow_null = True
    )

    principal = serializers.BooleanField(required = False)

    class Meta:
        """Contact meta class."""

        model = Contact

        fields = (
            'email',
            'area_code',
            'phone',
            'principal'
        )

    @transaction.atomic
    def create(self, data):
        """Create new company contacts."""
        company = self.context['company']
        
        principal = data.pop("principal") if data.get("principal") else not bool(company.principal_contact)
        
        contact = Contact.objects.create(
            company = company,
            **data
        )

        if principal is True:
            company.principal_contact = contact
            company.save()

        return contact

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a company location."""
        company = self.context['company']

        principal = validated_data.pop("principal") if validated_data.get("principal") else not bool(company.principal_contact)

        updated_contact = super().update(instance, validated_data)
        
        if principal is True:
            company.principal_contact = updated_contact
            company.save()

        return updated_contact