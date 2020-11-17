# serializers/companies.py

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.db import transaction

# Models
from companies.models import Company, CompanyLocation, CompanySaleLocation, Contact, VisibilityState
from django.contrib.auth import get_user_model
from multimedia.models import Image
from multimedia.serializers.images import ImageModelSerializer
from users.models import Verification

# Serializers
from companies.serializers.locations import (
    CompanyLocationNestedModelSerializer, CompanySaleLocationModelSerializer, 
    UpdateCompanySummarySaleLocationSerializer, HandleCompanySaleLocationSerializer,
    HandleCompanyLocationSerializer
)
from companies.serializers.contacts import ContactModelSerializer, HandleCompanyContactSerializer


class CompanyModelSerializer(serializers.ModelSerializer):

    logo = ImageModelSerializer(required = False)

    class Meta:
        model = Company
        fields = ('id', 'name', 'nit', 'industry', 'logo', 'role', 'web_url', 
            'description' , 'principal_contact', 'principal_location')


class SignupCompanyModelSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        max_length=60,
        validators=[
            UniqueValidator(queryset=Company.objects.all(), message = "There is alredy a company with this name")
        ]
    )

    nit = serializers.CharField(
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

    class Meta:
        model = Company
        fields = ('id', 'name', 'nit', 'industry')


class ProductCompanyModelSerializer(serializers.ModelSerializer):
    """Model serializer for display the company in the product detail."""

    principal_contact = ContactModelSerializer()

    class Meta:
        
        model = Company

        fields = (
            'id',
            'name',
            'user__username',
            'principal_contact'
        )


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


class CompanySummarySerializer(serializers.ModelSerializer):
    """Serializer of the identity summary of a company."""

    principal_location = CompanyLocationNestedModelSerializer()

    principal_contact = ContactModelSerializer()

    sale_locations = serializers.SerializerMethodField()

    class Meta:
        model = Company

        fields = ('id', 'name', 'industry', 'description', 'web_url',
            'principal_location', 'principal_contact', 'sale_locations')


    def get_sale_locations(self, instance):
        company_sale_locations = CompanySaleLocation.objects.filter( 
            company = instance, visibility = VisibilityState.OPEN.value)
        
        return CompanySaleLocationModelSerializer(company_sale_locations, many = True).data


class UpdateCompanySummarySerializer(serializers.ModelSerializer):
    """Serializer for update the identity summary of a company."""

    requires_context = True

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    industry = serializers.CharField(max_length=60)

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

    principal_location = HandleCompanyLocationSerializer(required = False)

    principal_contact = ContactModelSerializer(required = False)

    sale_locations = UpdateCompanySummarySaleLocationSerializer(many = True, required = False)

    class Meta:
        model = Company

        fields = ('name', 'industry', 'description', 'web_url',
            'principal_location', 'principal_contact', 'sale_locations')

    @transaction.atomic
    def update(self, instance, validated_data):
        """Customize the update function for the serializer to update the
            related_field values.
        """
        company = self.context["company"]

        if 'principal_location' in validated_data:
            principal_location = validated_data.pop("principal_location")
            self.create_or_update_principal_location(company, principal_location)

        if 'sale_locations' in validated_data:
            sale_locations = validated_data.pop("sale_locations")
            self.create_or_update_sale_locations(company, sale_locations)

        if 'pricipal_contact' in validated_data:
            pricipal_contact = validated_data.pop("pricipal_contact")
            self.create_or_update_principal_contact(company, pricipal_contact)

        return super().update(instance, validated_data)

    
    def create_or_update_principal_location(self, company, principal_location):
        """Create or update the principal location of the company by param."""
        company_location = company.principal_location

        if company_location:
            location_serializer = HandleCompanyLocationSerializer(
                instance = company_location, data = principal_location, 
                partial = True, context = {"company": company}
            )
        else:
            location_serializer = HandleCompanyLocationSerializer(
                data = principal_location, context = {"company": company}
            )

        location_serializer.is_valid(raise_exception = True)
        location_serializer.save()

    
    def create_or_update_sale_locations(self, company, sale_locations):
        """Create or update the sales locations of the company by param."""
        for location in sale_locations:
            if location.get("id") is None:
                sale_location_serializer = HandleCompanySaleLocationSerializer(
                    data = location, context = {"company": company}
                )
                sale_location_serializer.is_valid(raise_exception = True)
                sale_location_serializer.save()
            else:
                company_sale_location = CompanySaleLocation.objects.get( 
                    id = location.get("id"), company = company )
                
                if company_sale_location is not None:
                    sale_location_serializer = HandleCompanySaleLocationSerializer(
                        instance = company_sale_location, data = location, partial = True
                    )
                    sale_location_serializer.is_valid(raise_exception = True)
                    sale_location_serializer.save()


    def create_or_update_principal_contact(self, company, principal_contact):
        """Create or update the contact channel of the company by param."""
        company_contact = company.principal_contact

        if company_contact:
            contact_serializer = HandleCompanyContactSerializer(
                instance = company_contact, data = principal_contact, 
                partial = True, context = {"company": company}
            )
        else:
            contact_serializer = HandleCompanyContactSerializer(
                data = principal_contact, context = {"company": company}
            )

        contact_serializer.is_valid(raise_exception = True)
        contact_serializer.save()