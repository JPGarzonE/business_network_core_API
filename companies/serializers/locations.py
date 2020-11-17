"""Locations serializer."""

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from companies.models import CompanyLocation, CompanySaleLocation, Image
from multimedia.serializers.images import ImageModelSerializer

class CompanyLocationModelSerializer(serializers.ModelSerializer):
    """Company Location model serializer."""

    headquarters_image = ImageModelSerializer()

    class Meta:
        """Location meta class."""

        model = CompanyLocation

        fields = (
            'id',
            'company',
            'country',
            'city',
            'region',
            'address',
            'zip',
            'headquarters_image',
        )

        read_only_fields = (
            'company',
            'headquarters_image',
        )


class CompanyLocationNestedModelSerializer(serializers.ModelSerializer):
    """Company location nested model serializer."""

    class Meta:
        """Location meta class."""

        model = CompanyLocation

        fields = (
            'id',
            'country',
            'city',
            'region',
            'address',
            'zip',
        )


class CompanySaleLocationModelSerializer(serializers.ModelSerializer):
    """Company Sale Location model serializer."""

    class Meta:
        """Company Sale Location meta class."""

        model = CompanyLocation

        fields = (
            'id',
            'company',
            'country',
            'city',
            'region'
        )

        read_only_fields = (
            'company',
        )


class UpdateCompanySummarySaleLocationSerializer(serializers.Serializer):
    """Company Sale Location serializer for updating company summary"""

    id = serializers.IntegerField()

    country = serializers.CharField(
        min_length = 2,
        max_length = 40
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )


class HandleCompanyLocationSerializer(serializers.ModelSerializer):
    """Create and update company location"""

    requires_context = True

    country = serializers.CharField(
        min_length = 2,
        max_length = 40
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    address = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    zip = serializers.CharField(
        min_length = 2,
        max_length = 10,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    headquarters_image_id = serializers.IntegerField(required = False)

    principal = serializers.BooleanField( required = False,
        help_text = "Attribute to indicate if its the main location of a user (Company)")

    class Meta:
        """Company Location meta class."""

        model = CompanyLocation

        fields = (
            'country',
            'city',
            'region',
            'address',
            'zip',
            'headquarters_image_id',
            'principal',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company location."""
        company = self.context['company']
        
        principal = data.pop("principal") if data.get("principal") else not bool(company.principal_location)
        
        headquarters_image = None
        if data.get('headquarters_image_id'):
            image_id = data.pop("headquarters_image_id")
            try:
                headquarters_image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'headquarters_image_id'")

        location = CompanyLocation.objects.create(
            company = company,
            **data
        )

        if principal is True:
            company.principal_location = location
            company.save()
        
        if headquarters_image:
            location.headquarters_image = headquarters_image
            location.save()

        return location
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a company location."""
        company = self.context['company']

        if validated_data.get('headquarters_image_id'):
            image_id = validated_data.pop("headquarters_image_id")
            try:
                headquarters_image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'headquarters_image_id'")

            instance.headquarters_image = headquarters_image

        principal = validated_data.pop("principal") if validated_data.get("principal") else not bool(company.principal_location)

        updated_location = super().update(instance, validated_data)

        if principal is True:
            company.principal_location = updated_location
            company.save()

        return updated_location


class HandleCompanySaleLocationSerializer(serializers.ModelSerializer):
    """Creates and update company sales location."""

    requires_context = True

    country = serializers.CharField(
        min_length = 2,
        max_length = 40
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    class Meta:
        """Company Sale Location meta class."""

        model = CompanyLocation

        fields = (
            'country',
            'city',
            'region'
        )

    def create(self, data):
        """Create new company sale location."""

        company = self.context['company']

        location = CompanySaleLocation.objects.create(
            company = company,
            **data
        )

        return location