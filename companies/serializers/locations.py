"""Locations serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Location

class LocationModelSerializer(serializers.ModelSerializer):
    """Location model serializer."""

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
            'principal',
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
        required = False
    )

    address = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False
    )

    zip = serializers.CharField(
        min_length = 2,
        max_length = 10,
        required = False
    )

    principal = serializers.BooleanField(required = False)

    def create(self, data):
        """Create new company location."""
        company = self.context['company']
        
        location = Location.objects.create(
            company = company,
            **data
        )

        return location