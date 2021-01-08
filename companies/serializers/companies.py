# Serializers companies

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.db import transaction

# Models
from ..models import Company
from multimedia.models import Image

# Serializers
from multimedia.serializers import ImageModelSerializer


def generate_company_accountname(company_name):
    """Recieve the name of the company and generate a valid accountname for it."""
    accountname_lower = company_name.lower()
    generated_accountname = accountname_lower.strip().replace(" ", ".")
    i = 0
    while True:
        accountname = generated_accountname if i == 0 else generated_accountname + str(i)
        try:
            Company.objects.get( accountname = accountname )
        except Company.DoesNotExist:
            break
        
        i += 1
    
    return accountname


class CompanyModelSerializer(serializers.ModelSerializer):

    logo = ImageModelSerializer(required = False)

    class Meta:
        model = Company

        fields = (
            'id', 
            'accountname',
            'name', 
            'legal_identifier', 
            'description' ,
            'is_buyer',
            'is_supplier',
            'is_verified',
            'logo',
            'register_date',
        )


class SignupDocumentationResponseSerializer(serializers.Serializer):
    """Serializer created uniquely for display correctly 
    the response data of the signup endpoints"""

    company = CompanyModelSerializer()

    access_token = serializers.CharField()


class UpdateCompanySerializer(serializers.ModelSerializer):
    """Modelserializer for update a company"""

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    legal_identifier = serializers.CharField(
        max_length = 13,
        validators = [
            RegexValidator(regex = r'(\d{9,9}((.)\d)?)', 
                message = "El identificar legal debe estar acorde al formato exigído"),
            UniqueValidator(queryset=Company.objects.all())
        ]
    )

    logo_id = serializers.IntegerField(required = False)

    description = serializers.CharField(
        max_length = 155,
        required = False,
        allow_null = True
    )

    class Meta:
        model = Company
        fields = (
            'name', 
            'legal_identifier', 
            'logo_id',
            'description'
        )

        read_only_fields = (
            'id', 'is_buyer', 'is_supplier', 'is_verified'
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        """Customize the update function for the serializer to update the
            related_field values.
        """
        if 'logo_id' in validated_data:
            image_id = validated_data.pop("logo_id")
            try:
                image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in 'logo_id'" )

            if image :
                instance.logo = image
        
        company_updated = super().update(instance, validated_data)

        return company_updated