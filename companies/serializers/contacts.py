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
            'phone',
            'ext_phone',
            'principal'
        )

class HandleCompanyContactSerializer(serializers.ModelSerializer):
    """Create and update company contact."""

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

    class Meta:
        """Contact meta class."""

        model = Contact

        fields = (
            'email',
            'phone',
            'ext_phone',
            'principal'
        )

    @transaction.atomic
    def create(self, data):
        """Create new company contacts."""
        company = self.context['company']

        first_principal_contact = Contact.objects.filter( company = company, principal = True )

        if data.get("principal"):
            principal = data.pop("principal")

            if first_principal_contact:
                first_principal_contact = first_principal_contact[0]
                first_principal_contact.principal = False
                first_principal_contact.save()
        else:
            if not first_principal_contact:
                principal = True
            else:
                principal = False
        
        contact = Contact.objects.create(
            company = company,
            principal = principal,
            **data,
        )

        return contact

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a company location."""
        company = self.context['company']
        principal = validated_data.get("principal")

        if principal is True:
            first_principal_contact = Contact.objects.filter( company = company, principal = True )

            if first_principal_contact:
                for contact in first_principal_contact:
                    contact.principal = False
                    contact.save()

            instance.principal = validated_data.pop("principal")

        return super().update(instance, validated_data)