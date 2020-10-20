"""Products serializer."""

# Django
from django.db import transaction
from django.db.utils import IntegrityError

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Certificate, Currency, Product, ProductCertificate, ProductImage
from multimedia.models import Image

# Serializers
from companies.serializers import CertificateModelSerializer, CurrencyModelSerializer
from multimedia.serializers.images import ImageModelSerializer


class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    minimum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)
    maximum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)
    
    price_currency = CurrencyModelSerializer(allow_null = True)
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
            'price_currency',
            'tariff_heading',
            'minimum_purchase',
            'description',
            'certificates',
            'images'
        )

        read_only_fields = (
            'company',
            'minimum_price',
            'maximum_price',
            'price_currency',
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

    minimum_price = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        required = True
    )

    maximum_price = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        required = False,
    )

    tariff_heading = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    minimum_purchase = serializers.CharField(
        min_length = 0,
        max_length = 20,
        required = True
    )

    currency_id = serializers.IntegerField(
        help_text = "Id that determine the currency of the prices in the product. For seeing which currencies are available look the 'currencies/' endpoint."
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
            'currency_id',
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
        currency = None

        if 'images' in data:
            images = data.pop('images')

        if 'certificates' in data:
            certificates = data.pop('certificates')

        currency_id = data.pop('currency_id')
        try:
            currency = Currency.objects.get( id = currency_id )
        except Currency.DoesNotExist:
            raise Exception("Theres no currency with the id provided in 'currency_id' attribute")

        product = Product.objects.create(
            company = company,
            price_currency = currency,
            **data
        )

        if images and product:
            self.create_product_images(product, images)
        
        if certificates and product:
            self.create_product_certificates(product, certificates)

        return product


    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Customize the update function for the serializer to update the
            related_field values.
        """

        if 'images' in validated_data and instance:
            self.create_product_images(instance, validated_data.pop('images'))
        
        if 'certificates' in validated_data and instance:
            self.create_product_certificates(instance, validated_data.pop('certificates'))

        product_updated = super().update(instance, validated_data)     

        return product_updated

    # certificates is an array with the ids of the certificates
    # product is the instance created previously
    def create_product_certificates(self, product, certificates):
        for idx, certificate_id in enumerate(certificates):
            try:
                certificate_object = Certificate.objects.get( id = certificate_id )
            except Certificate.DoesNotExist:
                raise Exception( "Theres no certificate with the id provided in certificates[{}]".format(idx) )

            try:
                ProductCertificate.objects.create( product = product, certificate = certificate_object )
            except IntegrityError:
                raise Exception( "The certificate with id provided in certificates[{}] is repeated".format(idx) )

    
    # images is an array with the ids of the images
    # product is the instance created previously
    def create_product_images(self, product, images):
        for idx, image_id in enumerate(images):
            try:
                image_object = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception( "Theres no image with the id provided in images[{}]".format(idx) )
            
            try:
                ProductImage.objects.create( product = product, image = image_object )
            except IntegrityError:
                raise Exception( "The image with id provided in images[{}] is repeated".format(idx) )