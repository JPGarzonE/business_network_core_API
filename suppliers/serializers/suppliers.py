# Serializers suppliers

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
from companies.models import Company, CompanyMember, CompanyVerification, CompanyVerificationFile
from ..models import SupplierProfile, SupplierLocation, SupplierSaleLocation
from multimedia.models import File

# Serializers
from companies.serializers import CompanyModelSerializer
from .locations import (
    SupplierLocationNestedModelSerializer, SupplierSaleLocationModelSerializer, 
    UpdateSupplierSummarySaleLocationSerializer, HandleSupplierSaleLocationSerializer,
    HandleSupplierLocationSerializer
)


class ActivateSupplierSerializer(serializers.ModelSerializer):
    """
    Serializer to take a company and extends 
    its capabilites for being a supplier.
    """

    company = CompanyModelSerializer( required = False )

    class Meta:
        model = SupplierProfile
        
        fields = ('id', 'company', 'display_name', 'description',
            'industry', 'contact_area_code', 'contact_phone', 
            'contact_email', 'activation_date' , 'principal_location'
        )

        read_only_fields = ('id', 'company', 'display_name', 'description',
            'industry', 'contact_area_code', 'contact_phone', 
            'contact_email', 'activation_date' , 'principal_location'
        )

    @transaction.atomic
    def create(self, validated_data):
        company = self.context.pop('company')

        company.is_supplier = True
        company.save()

        return SupplierProfile.objects.create(
            company = company,
            **validated_data
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
            supplier = instance
        )
        
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