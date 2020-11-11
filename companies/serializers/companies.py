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

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    nit = RegexValidator(
        regex = r'(\d{9,9}((.)\d)?)',
        message = "El nit debe estar acorde al formato de la registraduria"
    )

    industry = serializers.CharField(max_length=60)

    logo = ImageModelSerializer(required = False)

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

    principal_location = serializers.SerializerMethodField()

    sale_locations = serializers.SerializerMethodField()

    contact_channel = serializers.SerializerMethodField()

    class Meta:
        model = Company

        fields = ('id', 'name', 'industry', 'description', 'web_url',
            'principal_location', 'sale_locations', 'contact_channel')


    def get_principal_location(self, instance):
        try:
            company_location = CompanyLocation.objects.get( company = instance, visibility = VisibilityState.OPEN.value, 
                principal = True )

            return CompanyLocationNestedModelSerializer(company_location).data
        except CompanyLocation.DoesNotExist:
            return None

    def get_sale_locations(self, instance):
        company_sale_locations = CompanySaleLocation.objects.filter( 
            company = instance, visibility = VisibilityState.OPEN.value)
        
        return CompanySaleLocationModelSerializer(company_sale_locations, many = True).data

    def get_contact_channel(self, instance):
        try:
            contact_channel = Contact.objects.get( company = instance, visibility = VisibilityState.OPEN.value,
                principal = True )

            return ContactModelSerializer(contact_channel).data            
        except Contact.DoesNotExist:
            return None


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

    principal_location = CompanyLocationNestedModelSerializer(required = False)

    sale_locations = UpdateCompanySummarySaleLocationSerializer(many = True, required = False)

    contact_channel = ContactModelSerializer(required = False)

    class Meta:
        model = Company

        fields = ('name', 'industry', 'description', 'web_url',
            'principal_location', 'sale_locations', 'contact_channel')

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

        if 'contact_channel' in validated_data:
            contact_channel = validated_data.pop("contact_channel")
            self.create_or_update_contact_channel(company, contact_channel)

        return super().update(instance, validated_data)

    
    def create_or_update_principal_location(self, company, principal_location):
        """Create or update the principal location of the company by param."""
        try:
            company_location = CompanyLocation.objects.get( company = company, principal = True )
            
            location_serializer = HandleCompanyLocationSerializer(
                instance = company_location, data = principal_location, 
                partial = True, context = {"company": company}
            )
            location_serializer.is_valid(raise_exception = True)
            location_serializer.save()
        except CompanyLocation.DoesNotExist:
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


    def create_or_update_contact_channel(self, company, contact_channel):
        """Create or update the contact channel of the company by param."""
        try:
            company_contact = Contact.objects.get( company = company, principal = True )
            
            contact_serializer = HandleCompanyContactSerializer(
                instance = company_contact, data = contact_channel, 
                partial = True, context = {"company": company}
            )
            contact_serializer.is_valid(raise_exception = True)
            contact_serializer.save()
        except Contact.DoesNotExist:
            contact_serializer = HandleCompanyContactSerializer(
                data = contact_channel, context = {"company": company}
            )
            contact_serializer.is_valid(raise_exception = True)
            contact_serializer.save()