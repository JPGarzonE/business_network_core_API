"""Products serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Product, Media
from companies.serializers.media import MediaModelSerializer

class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    media = MediaModelSerializer()

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'id',
            'company',
            'category',
            'name',
            'price',
            'description',
            'media'
        )

        read_only_fields = (
            'company'
            'media',
        )



class CreateCompanyProductSerializer(serializers.Serializer):
    """Create company service"""

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

    price = serializers.CharField(
        min_length = 2,
        max_length = 20,
        required = False
    )

    media = MediaModelSerializer( required = False )

    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        media = None

        if( data.get('media') ):
            media_data = data.pop("media")
            media = Media.objects.create( **media_data )

        data['media'] = media
        product = Product.objects.create(
            company = company,
            **data
        )

        return product