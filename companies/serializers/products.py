"""Products serializer."""

# Django
from django.db import transaction
from django.db.utils import IntegrityError

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Certificate, Product, ProductCertificate, ProductImage
from multimedia.models import Image

# Serializers
from companies.serializers import CertificateModelSerializer
from multimedia.serializers.images import ImageModelSerializer


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    certificates = CertificateModelSerializer(many = True)
    images = ImageModelSerializer(many = True)

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
            'images'
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

    images = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the images (previously uploaded)"
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
            'images'
        )

        read_only_fields = (
            'id',
            'certificates',
            'images',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        images = None
        certificates = None

        if 'images' in data:
            images = data.pop('images')

        if 'certificates' in data:
            certificates = data.pop('certificates')

        product = Product.objects.create(
            company = company,
            **data
        )

        if images and product:
            for idx, image_id in enumerate(images):
                try:
                    image_object = Image.objects.get( id = image_id )
                except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in images[{}]".format(idx) )
                
                try:
                    ProductImage.objects.create( product = product, image = image_object )
                except IntegrityError:
                    raise Exception( "The image with id provided in images[{}] is repeated".format(idx) )
        
        if certificates and product:
            for idx, certificate_id in enumerate(certificates):
                try:
                    certificate_object = Certificate.objects.get( id = certificate_id )
                except Certificate.DoesNotExist:
                    raise Exception( "Theres no certificate with the id provided in certificates[{}]".format(idx) )

                try:
                    ProductCertificate.objects.create( product = product, certificate = certificate_object )
                except IntegrityError:
                    raise Exception( "The certificate with id provided in certificates[{}] is repeated".format(idx) )

        return product


    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Customize the update function for the serializer to update the
            related_field values.
        """

        if 'images' in validated_data:
            images = validated_data.pop('images')

            for idx, image_id in enumerate(images):
                try:
                    image_object = Image.objects.get( id = image_id )
                except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in images[{}]".format(idx) )

                try:
                    ProductImage.objects.create( product = instance, image = image_object )
                except IntegrityError:
                    raise Exception( "The image with id provided in images[{}] is alredy in this product".format(idx) )
        
        if 'certificates' in validated_data:
            certificates = validated_data.pop('certificates')

            for idx, certificate_id in enumerate(certificates):
                try:
                    certificate_object = Certificate.objects.get( id = certificate_id )
                except Certificate.DoesNotExist:
                    raise Exception( "Theres no certificate with the id provided in certificates[{}]".format(idx) )

                try:
                    ProductCertificate.objects.create( product = instance, certificate = certificate_object )
                except IntegrityError:
                    raise Exception( "The certificate with id provided in certificates[{}] is alredy in this product".format(idx) )

        product_updated = super().update(instance, validated_data)     

        return product_updated