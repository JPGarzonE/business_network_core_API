"""Locations serializer."""

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from companies.models import Location, Image
from multimedia.serializers.images import ImageModelSerializer

class LocationModelSerializer(serializers.ModelSerializer):
    """Location model serializer."""

    headquarters_image = ImageModelSerializer()

    class Meta:
        """Location meta class."""

        model = Location

        fields = (
            'id',
            'company',
            'country',
            'city',
            'region',
            'address',
            'zip',
            'headquarters_image',
            'principal',
        )

        read_only_fields = (
            'company',
            'headquarters_image',
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
        max_length = 40
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
        """Location meta class."""

        model = Location

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

        first_principal_location = Location.objects.filter( company = company, principal = True )

        if data.get("principal"):
            principal = data.pop("principal")
            
            if first_principal_location:
                first_principal_location = first_principal_location[0]
                first_principal_location.principal = False
                first_principal_location.save()
        else:
            if not first_principal_location:
                principal = True
            else:
                principal = False

        headquarters_image = None

        if data.get('headquarters_image_id'):
            image_id = data.pop("headquarters_image_id")
            try:
                headquarters_image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'headquarters_image_id'")

        location = Location.objects.create(
            company = company,
            principal = principal,
            **data
        )
        
        if headquarters_image:
            location.headquarters_image = headquarters_image
            print(location.headquarters_image)
            location.save()

        return location
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a company location."""
        company = self.context['company']
        principal = validated_data.get("principal")

        if principal is True:
            first_principal_location = Location.objects.filter( company = company, principal = True )

            if first_principal_location:
                for location in first_principal_location:
                    location.principal = False
                    location.save()

            instance.principal = validated_data.pop("principal")

        if validated_data.get('headquarters_image_id'):
            image_id = validated_data.pop("headquarters_image_id")
            try:
                headquarters_image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'headquarters_image_id'")

            instance.headquarters_image = headquarters_image

        return super().update(instance, validated_data)