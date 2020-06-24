"""Locations serializer."""

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from companies.models import Location, Media
from multimedia.serializers.media import MediaModelSerializer

class LocationModelSerializer(serializers.ModelSerializer):
    """Location model serializer."""

    media = MediaModelSerializer()

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
            'media',
            'principal',
        )

        read_only_fields = (
            'company'
            'media',
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a company location."""
        company = self.context['company']
        first_principal_location = Location.objects.filter( company = company, principal = True )

        principal = validated_data.get("principal")

        if principal is True:
            if first_principal_location:
                for location in first_principal_location:
                    location.principal = False
                    location.save()

            instance.principal = validated_data.pop("principal")
            instance.save()

        return super().update(instance, validated_data)

class CreateCompanyLocationSerializer(serializers.Serializer):
    """Create company location"""

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
        allow_null = True
    )

    address = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True
    )

    zip = serializers.CharField(
        min_length = 2,
        max_length = 10,
        required = False,
        allow_null = True
    )

    media = MediaModelSerializer( required = False )

    principal = serializers.BooleanField( required = False )

    @transaction.atomic
    def create(self, data):
        """Create new company location."""
        company = self.context['company']

        first_principal_location = Location.objects.filter( company = company, principal = True )

        if data.get("principal"):
            principal = data.pop("principal")
            if principal:
                if first_principal_location:
                    first_principal_location = first_principal_location[0]
                    first_principal_location.principal = False
                    first_principal_location.save()
                principal = True
            else:
                principal = False
        else:
            if not first_principal_location:
                principal = True
            else:
                principal = False

        media = None

        if data.get('media'):
            media_data = data.pop("media")
            media = Media.objects.create( **media_data )

        data['media'] = media

        location = Location.objects.create(
            company = company,
            principal = principal,
            **data
        )

        return location