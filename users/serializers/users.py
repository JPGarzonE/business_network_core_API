# serializers.py

# Django
from django.contrib.auth import password_validation, authenticate
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.utils import timezone

# Models
from users.models import User
from companies.models import Company
from users.models import Verification
from companies.serializers import CompanyModelSerializer

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Utilities
# import jwt

class UserModelSerializer(serializers.ModelSerializer):

    company = CompanyModelSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'company',)


class UserSignupSerializer(serializers.Serializer):
    """User sign up serializer.

    Handle sign up data validation and user/profile creation.
    """
    email = serializers.EmailField(
        validators = [ UniqueValidator( queryset = User.objects.all() ) ]
    )

    company = CompanyModelSerializer()

    # password
    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Validate that passwords match"""
        passw = data['password']
        passw_conf = data['password_confirmation']

        if passw != passw_conf:
            raise serializers.ValidationError("Las contraseñas no concuerdan")
        
        password_validation.validate_password( passw )
        
        return data

    def create(self, data):
        """Handle user and profile creation"""
        data.pop('password_confirmation')
        company_data = data.pop("company")

        data_username = company_data.get("name")
        username_lower = data_username.lower()
        username = username_lower.strip().replace(" ", ".")
        data["username"] = username

        verification = Verification.objects.create( verified = False, state = "none" )
        company_data["verification"] = verification

        try:
            Company.objects.create( user = user, **company_data )
        except UnboundLocalError:
            user = User.objects.create_user(**data, is_verified = True, is_client = True)
            Company.objects.create( user = user, **company_data )

        return user

class UserLoginSerializer(serializers.Serializer):
    """ User Login Serializer

    Handle the login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length = 8, max_length = 64)

    def validate(self, data):
        """Check credentials."""
        user = authenticate( username = data['email'], password = data['password'] )

        if not user:
            raise serializers.ValidationError('Invalid credentials')        
        if not user.is_verified:
            raise serializers.ValidationError('Account is not verified yet')
        
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        token, created = Token.objects.get_or_create( user = self.context['user'] )
        return self.context['user'], token.key
    