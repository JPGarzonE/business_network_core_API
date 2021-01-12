# Serializers suppliers

# Constants
from companies.constants import VisibilityState

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

# Django
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

# Send email
from companies.serializers.verifications import send_company_verification_notification_email

# Models
from companies.models import User, Company, CompanyMember, CompanyVerification, CompanyVerificationFile
from ..models import SupplierProfile, SupplierLocation, SupplierSaleLocation
from multimedia.models import File

# Serializers
from .locations import (
    SupplierLocationNestedModelSerializer, SupplierSaleLocationModelSerializer, 
    UpdateSupplierSummarySaleLocationSerializer, HandleSupplierSaleLocationSerializer,
    HandleSupplierLocationSerializer
)


class SupplierProfileModelSerializer(serializers.ModelSerializer):
    """Model serializer for the supplier profile model."""

    class Meta:
        model = SupplierProfile
        
        fields = (
            'id', 
            'company',
            'display_name', 
            'description',
            'industry', 
            'contact_area_code', 
            'contact_phone', 
            'contact_email',   
            'activation_date' , 
            'principal_location'
        )


class SignupSupplierSerializer(serializers.Serializer):
    """Serializer for the signup of a supplier."""

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

    industry = serializers.CharField(max_length=60)

    comercial_certificate_id = serializers.IntegerField(required = False)

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

        certificate = None
        if data.get('comercial_certificate_id'):
            certificate_id = data.pop("comercial_certificate_id")
            certificate = File.objects.get( id = certificate_id )

            if certificate:
                verification = CompanyVerification.objects.create( 
                    state = CompanyVerification.States.INPROGRESS.value )

                company_verification_file = CompanyVerificationFile.objects.create(
                    company_verification = verification, file = certificate )
        else:
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
            verification = verification, is_supplier = True
        )

        SupplierProfile.objects.create(company = company, 
            display_name = company.name, industry = data.get('industry'))

        if certificate is not None and company_verification_file is not None:
            send_company_verification_notification_email(user, company, [certificate.path])

        token, created = Token.objects.get_or_create( user = user )
        return company, token.key


class ProductSupplierModelSerializer(serializers.ModelSerializer):
    """Model serializer for display the supplier in the product detail."""

    accountname = serializers.CharField(source="company.accountname")

    class Meta:
        
        model = SupplierProfile

        fields = (
            'id',
            'display_name',
            'accountname',
            'contact_area_code',
            'contact_phone',
            'contact_email'
        )


class UpdateSupplierSerializer(serializers.ModelSerializer):
    """Update a supplier"""

    display_name = serializers.CharField(max_length=60)

    industry = serializers.CharField(max_length=60, required = False)

    description = serializers.CharField(
        max_length = 155, required = False, allow_null = True, allow_blank = True
    )

    contact_area_code = serializers.CharField(
        max_length = 5, required = False, allow_blank = True, allow_null = True
    )

    contact_phone = serializers.CharField(
        max_length = 15, required = False, allow_blank = True, allow_null = True
    )

    contact_email = serializers.EmailField(required = False)

    class Meta:
        model = SupplierProfile
        fields = (
            'id', 
            'display_name',  
            'industry', 
            'description',
            'contact_area_code',
            'contact_phone',
            'contact_email'
        )


class SupplierSummarySerializer(serializers.ModelSerializer):
    """Serializer of the identity summary of a supplier."""

    principal_location = SupplierLocationNestedModelSerializer()

    sale_locations = serializers.SerializerMethodField()

    class Meta:
        model = SupplierProfile

        fields = (
            'display_name', 
            'industry', 
            'description', 
            'principal_location',
            'sale_locations'
        )


    def get_sale_locations(self, instance):
        supplier_sale_locations = SupplierSaleLocation.objects.filter( 
            supplier = instance, visibility = VisibilityState.OPEN.value)
        
        return SupplierSaleLocationModelSerializer(
            supplier_sale_locations,
            many = True
        ).data


class UpdateSupplierSummarySerializer(serializers.ModelSerializer):
    """Serializer for update the identity summary of a supplier."""

    requires_context = True

    display_name = serializers.CharField(max_length=60)

    industry = serializers.CharField(max_length=60, required = False)

    description = serializers.CharField(
        max_length = 150,
        required = False,
        allow_null = True
    )

    principal_location = HandleSupplierLocationSerializer(required = False)

    sale_locations = UpdateSupplierSummarySaleLocationSerializer(many = True, required = False)

    class Meta:
        model = SupplierProfile

        fields = (
            'display_name', 
            'industry', 
            'description', 
            'principal_location',
            'sale_locations'
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        """Customize the update function for the serializer to update the
            related_field values.
        """
        supplier = self.context["supplier"]

        if 'principal_location' in validated_data:
            principal_location = validated_data.pop("principal_location")
            self.create_or_update_principal_location(supplier, principal_location)

        if 'sale_locations' in validated_data:
            sale_locations = validated_data.pop("sale_locations")
            self.create_or_update_sale_locations(supplier, sale_locations)

        return super().update(instance, validated_data)

    
    def create_or_update_principal_location(self, supplier, principal_location):
        """Create or update the principal location of the supplier by param."""
        supplier_location = supplier.principal_location

        if supplier_location:
            location_serializer = HandleSupplierLocationSerializer(
                instance = supplier_location, data = principal_location, 
                partial = True, context = {"supplier": supplier}
            )
        else:
            location_serializer = HandleSupplierLocationSerializer(
                data = principal_location, context = {"supplier": supplier}
            )

        location_serializer.is_valid(raise_exception = True)
        location_serializer.save()

    
    def create_or_update_sale_locations(self, supplier, sale_locations):
        """Create or update the sales locations of the supplier by param."""

        for location in sale_locations:
            if location.get("id") is None:
                sale_location_serializer = HandleSupplierSaleLocationSerializer(
                    data = location, context = {"supplier": supplier}
                )
                sale_location_serializer.is_valid(raise_exception = True)
                sale_location_serializer.save()
            else:
                supplier_sale_location = SupplierSaleLocation.objects.get( 
                    id = location.get("id"), supplier = supplier )
                
                if supplier_sale_location is not None:
                    sale_location_serializer = HandleSupplierSaleLocationSerializer(
                        instance = supplier_sale_location, data = location, partial = True
                    )
                    sale_location_serializer.is_valid(raise_exception = True)
                    sale_location_serializer.save()