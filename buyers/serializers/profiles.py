# Serializer profiles

# Constants
from companies.constants import VisibilityState

# Django rest framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Models
from ..models import BuyerProfile
from companies.models import User, Company


class BuyerProfileSerializer(serializers.ModelSerializer):
    """Serializer for the profile of a buyer.
        It is a ModelSerializer but is not the model serializer
        of the BuyerProfile class, this is only a unified representation
        of the buyer profile for retrieve the data on one request.
    """

    company_legal_identifier = serializers.CharField(
        max_length = 13,
        validators = [
            RegexValidator(regex = r'(\d{9,9}((.)\d)?)', 
                message = "El identificador legal debe estar acorde al formato exigído"),
            UniqueValidator(queryset=Company.objects.all())
        ],
        source = 'company.legal_identifier'
    )

    class Meta:
        model = BuyerProfile

        fields = (
            'id',
            'company_legal_identifier',
            'display_name',
            'description',
            'contact_email',
            'contact_area_code',
            'contact_phone'
        )

