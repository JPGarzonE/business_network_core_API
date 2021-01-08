# Serializers unregistered_companies

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.db import transaction

# Models
from ..models import UnregisteredCompany


class UnregisteredCompanyModelSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        max_length=60
    )

    legal_identifier = serializers.CharField(
        max_length = 11,
        validators = [
            RegexValidator(
                regex = r'(\d{9,9}((.)\d)?)',
                message = "El identificar legal debe estar acorde al formato exigído"
            )
        ],

        required = False,
        allow_null = True,
        allow_blank = True
    )

    industry = serializers.CharField(max_length=60)

    email = serializers.EmailField(
        required = False,
        allow_null = True,
        allow_blank = True
    )

    country = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    is_contactable = serializers.BooleanField(
        default = False,
        required = False,
        allow_null = True
    )

    class Meta():
        model = UnregisteredCompany

        fields = (
            'id', 
            'name', 
            'legal_identifier', 
            'industry', 
            'email', 
            'country',
            'city',
            'is_contactable'
        )