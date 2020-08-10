"""Products serializer."""

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Product
from multimedia.models import Media
from multimedia.serializers.media import MediaModelSerializer

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



class HandleCompanyProductSerializer(serializers.ModelSerializer):
    """Create and update a company product"""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 50
    )

    category = serializers.CharField(
        min_length = 3,
        max_length = 60,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    description = serializers.CharField(
        max_length = 155,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    price = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True
    )

    media_id = serializers.IntegerField(required = False)

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'id',
            'category',
            'name',
            'price',
            'description',
            'media_id'
        )

        read_only_fields = (
            'id',
            'media_id',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        media = None

        if( data.get('media_id') ):
            media_id = data.pop("media_id")
            media = Media.objects.get( id = media_id )

        product = Product.objects.create(
            company = company,
            **data
        )

        if media:
            product.media = media
            product.save()

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        media = None

        if 'media_id' in validated_data :
            media_id = validated_data.pop('media_id')
            media = Media.objects.get( id = media_id )
            
            if media :
                instance.media = media

        product_updated = super().update(instance, validated_data)     

        return product_updated