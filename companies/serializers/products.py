"""Products serializer."""

# Django
from django.db import transaction

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


    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        media = None

        if( 'media' in validated_data ):
            media_data = validated_data.pop('media')
            media_instance = instance.media
            media_serializer = self.fields['media']

            media = media_serializer.update(instance = media_instance, validated_data = media_data)

        product_updated = super().update(instance, validated_data)

        if( media ):
            product_updated.media = media

        return product_updated




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
        max_length = 155,
        required = False,
        allow_null = True
    )

    price = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True
    )

    media = MediaModelSerializer(
        required = False,
        allow_null = True
    )

    @transaction.atomic
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