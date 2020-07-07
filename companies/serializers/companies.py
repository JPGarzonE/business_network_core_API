# serializers/companies.py

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.db import transaction

# Models
from companies.models import Company
from django.contrib.auth import get_user_model
from multimedia.models import Media
from multimedia.serializers.media import MediaModelSerializer
from users.models import Verification

class CompanyModelSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    nit = RegexValidator(
        regex = r'(\d{9,9}((.)\d)?)',
        message = "El nit debe estar acorde al formato de la registraduria"
    )

    industry = serializers.CharField(max_length=60)

    logo = MediaModelSerializer(required = False)

    role = serializers.CharField(max_length=50, required = False)

    priority = serializers.CharField(max_length=50, required = False)

    description = serializers.CharField(
        max_length = 150,
        required = False,
        allow_null = True
    )

    web_url = serializers.CharField(
        max_length = 70,
        required = False,
        allow_null = True
    )

    class Meta:
        model = Company
        fields = ('id', 'name', 'nit', 'industry', 'logo',
            'role', 'priority', 'web_url', 'description')


class UpdateCompanySerializer(serializers.ModelSerializer):
    """Update a company"""

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    nit = serializers.CharField(
        max_length = 13,
        validators = [
            RegexValidator(regex = r'(\d{9,9}((.)\d)?)', message = "El nit debe estar acorde al formato de la registraduria"),
            UniqueValidator(queryset=Company.objects.all())
        ]
    )

    industry = serializers.CharField(max_length=60, required = False)

    logo_id = serializers.IntegerField(required = False)

    description = serializers.CharField(
        max_length = 150,
        required = False,
        allow_null = True
    )

    web_url = serializers.CharField(
        max_length = 70,
        required = False,
        allow_null = True
    )

    class Meta:
        model = Company
        fields = ('id', 'name', 'nit', 'industry', 'logo_id',
            'web_url', 'description')

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        if 'logo_id' in validated_data:
            media_id = validated_data.pop("logo_id")
            media = Media.objects.get( id = media_id )

            if media :
                instance.logo = media
        
        company_updated = super().update(instance, validated_data)

        return company_updated