# Serializers buyers

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth import password_validation
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

# Models
from companies.models import Company, CompanyMember, CompanyVerification, CompanyMember
from users.models import User
from ..models import BuyerProfile

# Serializers
from companies.serializers import CompanyModelSerializer


class ActivateBuyerSerializer(serializers.ModelSerializer):
    """
    Serializer to take a company and extends
    its capabilites for being a buyer.
    """

    company = CompanyModelSerializer( required = False )

    class Meta:
        model = BuyerProfile

        fields = ('id', 'company', 'display_name', 'description', 
            'contact_area_code', 'contact_phone', 'contact_email'
        )

        read_only_fields = ('id', 'company', 'display_name', 'description', 
            'contact_area_code', 'contact_phone', 'contact_email'
        )

    @transaction.atomic
    def create(self, validated_data):
        company = self.context.pop('company')

        company.is_buyer = True
        company.save()

        return BuyerProfile.objects.create(
            company = company,
            **validated_data
        )


class BuyerProfileModelSerializer(serializers.ModelSerializer):
    """Model serializer for the buyer profile model."""

    class Meta:
        model = BuyerProfile

        fields = (
            'id',
            'company',
            'display_name',
            'description',
            'contact_area_code',
            'contact_phone',
            'contact_email',
            'activation_date'
        )

        read_only_fields = (
            'id', 'company', 'activation_date'
        )