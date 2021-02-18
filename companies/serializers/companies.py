# Serializers companies

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.contrib.auth import password_validation
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

# Models
from ..models import Company
from multimedia.models import Image
from users.models import User

# Serializers
from multimedia.serializers import ImageModelSerializer


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


class SignupAccessSerializer(serializers.Serializer):
    """
    Serializer that returns the access data of the user after signup.\n
    It returns the tokens for authorize its transactions,
    the user data and the company that has been created with the request.
    """

    from users.seralizers import (
        AuthenticationTokensResponseSerializer, 
        UserAuthenticationTokenSerializer,
        UserModelSerializer
    )

    tokens = AuthenticationTokensResponseSerializer()

    user = UserModelSerializer()

    access_company = CompanyModelSerializer()


class SignupSerializer(serializers.Serializer):
    """Serializer for the signup of a company."""

    email = serializers.EmailField(
        validators = [ 
            UniqueValidator( queryset = User.objects.all(), message = "There is alredy a user with this email" )
        ]
    )

    full_name = serializers.CharField(
        max_length = 50, 
        help_text = _("Complete real name of the user")
    )

    name = serializers.CharField(
        max_length = 60,
        help_text = _("Real name of the company"),
        validators=[
            UniqueValidator(queryset=Company.objects.all(), message = "There is alredy a company with this name")
        ]
    )

    legal_identifier = serializers.CharField(
        max_length = 11,
        validators = [
            RegexValidator(
                regex = r'(\d{9,9}((.)\d)?)',
                message = "El nit debe estar acorde al formato de la registraduria"
            ),
            UniqueValidator(queryset=Company.objects.all(), message = "There is alredy a company with this nit")
        ]
    )

    password = serializers.CharField(min_length=8, max_length=64)

    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Validate that passwords match"""
        passw = data['password']
        passw_conf = data['password_confirmation']

        if passw != passw_conf:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        password_validation.validate_password( passw )
        
        return data

    @transaction.atomic
    def create(self, data):
        """Handle company and user first creation."""
        from users.seralizers import UserAuthenticationTokenSerializer

        data.pop('password_confirmation')
        email = data.get('email')
        password = data.get('password')

        user = User.objects.create_user(
            email = email,
            full_name = data.get('full_name'),
            password = password
        )

        company, creator_membership = Company.objects.create(
            creator_user = user,
            name = data.get('name'),
            legal_identifier = data.get('legal_identifier')
        )

        user.set_default_membership(creator_membership)
        refresh_token = UserAuthenticationTokenSerializer().get_token(user)

        auth_tokens = {
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token)
        }

        return user, company, auth_tokens