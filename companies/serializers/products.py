"""Products serializer."""

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Certificate, Product, ProductCertificate, ProductMedia
from multimedia.models import Media

# Serializers
from companies.serializers import CertificateModelSerializer
from multimedia.serializers.media import MediaModelSerializer


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    certificates = CertificateModelSerializer(many = True)
    media = MediaModelSerializer(many = True)

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'id',
            'company',
            'category',
            'name',
            'minimum_price',
            'maximum_price',
            'tariff_heading',
            'minimum_purchase',
            'description',
            'certificates',
            'media'
        )

        read_only_fields = (
            'company',
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

    minimum_price = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True
    )

    maximum_price = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True
    )

    tariff_heading = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True
    )

    minimum_purchase = serializers.CharField(
        min_length = 0,
        max_length = 20
    )

    certificates = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the certificates (previously uploaded)"
    )

    media = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the media (previously uploaded)"
    )

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'id',
            'category',
            'name',
            'minimum_price',
            'maximum_price',
            'tariff_heading',
            'minimum_purchase',
            'description',
            'certificates',
            'media'
        )

        read_only_fields = (
            'id',
            'certificates',
            'media',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        if 'media' in data:
            media = data.pop('media')

        if 'certificates' in data:
            certificates = data.pop('certificates')

        product = Product.objects.create(
            company = company,
            **data
        )

        if media and product:
            for media_id in media:
                media_object = Media.objects.get( id = media_id )
                ProductMedia.objects.create( product = product, media = media_object )
        
        if certificates and product:
            for certificate_id in certificates:
                certificate_object = Certificate.objects.get( id = certificate_id )
                ProductCertificate.objects.create( product = product, certificates = certificate_object )

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Customize the update function for the serializer to update the
            related_field values.
        """

        if 'media' in validated_data:
            media = validated_data.pop('media')

            for media_id in media:
                media_object = Media.objects.get( id = media_id )
                ProductMedia.objects.create( product = instance, media = media_object )
        
        if 'certificates' in validated_data:
            certificates = validated_data.pop('certificates')

            for certificate_id in certificates:
                certificate_object = Certificate.objects.get( id = certificate_id )
                ProductCertificate.objects.create( product = instance, certificates = certificate_object )

        product_updated = super().update(instance, validated_data)     

        return product_updated