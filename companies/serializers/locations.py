"""Locations serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Location, Media
from companies.serializers.media import MediaModelSerializer

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

    def create(self, data):
        """Create new company location."""
        company = self.context['company']
        media = None

        if( data.get('media') ):
            media_data = data.pop("media")
            media = Media.objects.create( **media_data )

        data['media'] = media

        location = Location.objects.create(
            company = company,
            **data
        )

        return location