"""Dnaelement serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Dnaelement, Media
from companies.serializers.media import MediaModelSerializer

class DnaelementModelSerializer(serializers.ModelSerializer):
    """Dnaelement model serializer."""

    media = MediaModelSerializer()

    class Meta:
        """Dnaelement meta class."""

        model = Dnaelement

        fields = (
            'id',
            'company',
            'category',
            'name',
            'description',
            'media'
        )

        read_only_fields = (
            'company'
            'media',
        )



class CreateCompanyDnaelementSerializer(serializers.Serializer):
    """Create company Dnaelement"""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 50
    )

    category = serializers.CharField(
        min_length = 3,
        max_length = 60
    )

    description = serializers.CharField(
        min_length = 2,
        max_length = 155,
        required = False
    )

    media = MediaModelSerializer( required = False )

    def create(self, data):
        """Create new company Dnaelement."""
        company = self.context['company']
        media = None

        if( data.get('media') ):
            media_data = data.pop("media")
            media = Media.objects.create( **media_data )

        data['media'] = media

        dnaelement = Dnaelement.objects.create(
            company = company,
            **data
        )

        return dnaelement