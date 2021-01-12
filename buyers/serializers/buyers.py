# Serializers buyers

# Constants
from companies.constants import VisibilityState

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
from companies.models import Company, CompanyMember, User, CompanyVerification, CompanyMember
from ..models import BuyerProfile


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


class SignupBuyerSerializer(serializers.Serializer):
    """Serializer for the signup of a buyer."""

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
        """Handle supplier profile creation."""
        data.pop('password_confirmation')

        verification = CompanyVerification.objects.create( 
            state = CompanyVerification.States.NONE.value )

        user = User.objects.create_user(
            email = data.get('email'),
            full_name = data.get('full_name'), 
            password = data.get('password')
        )

        company = Company.objects.create(
            creator_user = user,
            name = data.get('name'),
            legal_identifier = data.get('legal_identifier'),
            verification = verification, is_buyer = True
        )

        BuyerProfile.objects.create(company = company, display_name = company.name)

        token, created = Token.objects.get_or_create( user = user )
        return company, token.key