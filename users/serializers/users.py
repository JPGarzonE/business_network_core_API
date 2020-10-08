# serializers.py

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from users.models import User
from companies.models import Company
from users.models import Verification
from multimedia.models import Document

# Serializers
from companies.serializers import CompanyModelSerializer, SignupCompanyModelSerializer
from users.serializers.verifications import VerificationModelSerializer

# Send email
from users.serializers.verifications import send_verification_notification_email

# Utils
from datetime import timedelta
from django.utils.translation import ugettext_lazy as _
import jwt


class UserModelSerializer(serializers.ModelSerializer):

    company = CompanyModelSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'is_verified', 'is_staff', 'company', )

class UserNestedModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'is_verified')

class UserSignupSerializer(serializers.Serializer):
    """User sign up serializer.

    Handle sign up data validation and user/profile creation.
    """
    email = serializers.EmailField(
        validators = [ 
            UniqueValidator( queryset = User.objects.all(), message = "There is alredy a user with this email" )
        ]
    )

    full_name = serializers.CharField(help_text = _("Complete real name of the user"))

    company = SignupCompanyModelSerializer()

    comercial_certificate_id = serializers.IntegerField(required = False)

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

    @transaction.atomic
    def create(self, data):
        """Handle user and profile creation"""
        data.pop('password_confirmation')
        company_data = data.pop("company")

        data_username = company_data.get("name")
        username_lower = data_username.lower()
        username = username_lower.strip().replace(" ", ".")
        data["username"] = username

        certificate = None
        if data.get("comercial_certificate_id"):
            certificate_id = data.pop("comercial_certificate_id")
            certificate = Document.objects.get( id = certificate_id )

            if certificate:
                verification = Verification.objects.create( state = "InProgress" )
                certificate.verification = verification
        else:
            verification = Verification.objects.create( state = "None" )
        
        data["verification"] = verification

        user = User.objects.create_user(**data, is_client = True)
        company = Company.objects.create( user = user, **company_data )

        verification.save()

        if certificate and certificate.verification == verification:
            send_verification_notification_email(user)

        token, created = Token.objects.get_or_create( user = user )
        return user, token.key

    

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
        
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        token, created = Token.objects.get_or_create( user = self.context['user'] )
        return self.context['user'], token.key
    
class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer"""

    token = serializers.CharField()

    def validate_token(self, data):
        """Verify token is valid."""

        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms = ['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')

        self.context['payload'] = payload
        return data

    @transaction.atomic
    def save(self):
        """Update user's verified status"""
        payload = self.context['payload']
        user = User.objects.get(username = payload['user'])
        user.is_verified = True
        user.save()

        verification = user.verification
        verification.verified = True
        verification.state = "Success"
        verification.finish_date = timezone.now()
        verification.save()