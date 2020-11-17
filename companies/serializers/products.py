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
from companies.serializers import CertificateModelSerializer, CurrencyModelSerializer, ProductCompanyModelSerializer
from multimedia.serializers.images import ImageModelSerializer

# Signals
from companies import signals


class ProductOverviewModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    minimum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)
    maximum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)
    
    price_currency = CurrencyModelSerializer(allow_null = True)
    principal_image = ImageModelSerializer()

    class Meta:

        model = Product

        fields = (
            'id',
            'name',
            'category',
            'minimum_price',
            'maximum_price',
            'price_currency',
            'principal_image'
        )

        read_only_fields = (
            'price_currency',
            'principal_image'
        )


class ProductDetailModelSerializer(serializers.ModelSerializer):
    """Model serializer for the product detail."""    

    minimum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)
    maximum_price = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null = True)

    price_currency = CurrencyModelSerializer(allow_null = True)
    certificates = CertificateModelSerializer(many = True)
    principal_image = ImageModelSerializer()
    secondary_images = ImageModelSerializer(many = True)

    company = ProductCompanyModelSerializer()

    class Meta:

        model = Product

        fields = (
            'id',
            'name',
            'category',
            'minimum_price',
            'maximum_price',
            'price_currency',
            'measurement_unit',
            'tariff_heading',
            'minimum_purchase',
            'description',
            'certificates',
            'principal_image',
            'secondary_images',
            'company',
        )

        read_only_fields = (
            'company',
            'price_currency',
            'certificates',
            'principal_image',
            'secondary_images'
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

    currency_id = serializers.IntegerField(
        help_text = "Id that determine the currency of the prices in the product. For seeing which currencies are available look the 'currencies/' endpoint."
    )

    measurement_unit = serializers.CharField(
        max_length = 30,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    minimum_purchase = serializers.CharField(
        min_length = 0,
        max_length = 30,
        required = True
    )

    tariff_heading = serializers.CharField(
        min_length = 0,
        max_length = 20,
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

    certificates = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the certificates (previously uploaded)"
    )

    principal_image_id = serializers.IntegerField(
        help_text = "Id of the principal image of the product (previosuly uploaded)"
    )

    secondary_images = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the images (previously uploaded)"
    )

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'name',
            'category',
            'minimum_price',
            'maximum_price',
            'currency_id',
            'measurement_unit',
            'tariff_heading',
            'minimum_purchase',
            'description',
            'certificates',
            'principal_image_id',
            'secondary_images'
        )

        read_only_fields = (
            'certificates',
            'principal_image_id',
            'secondary_images'
        )

    @transaction.atomic
    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        principal_image_id = data.pop("principal_image_id") if 'principal_image_id' in data else None
        secondary_images = data.pop('secondary_images') if 'secondary_images' in data else None
        certificates = data.pop('certificates') if 'certificates' in data else None
        currency = None

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

        if principal_image_id and product:
            self.create_principal_product_image(product, principal_image_id)

        if secondary_images and product:
            self.create_secondary_product_images(product, secondary_images)
        
        if certificates and product:
            self.create_product_certificates(product, certificates)

        signals.post_product_create.send(sender = Product, instance = product, created = True)

        return product


    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Customize the update function for the serializer to update the
            related_field values.
        """

        if 'principal_image_id' in validated_data and instance:
            self.create_principal_product_image(instance, validated_data.pop('principal_image_id'))

        if 'secondary_images' in validated_data and instance:
            self.create_secondary_product_images(instance, validated_data.pop('secondary_images'))
        
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

    # image_id is the id of the image to associate
    # product is the instance created previously
    def create_principal_product_image(self, product, image_id):
        try:
            image_object = Image.objects.get( id = image_id )
            product.principal_image = image_object
            product.save()
        except Image.DoesNotExist:
            raise Exception( "Theres no image with the id provided in principal_image_id" )
    
    # images is an array with the ids of the secondary images
    # product is the instance created previously
    def create_secondary_product_images(self, product, images):
        for idx, image_id in enumerate(images):
            try:
                image_object = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception( "Theres no image with the id provided in secondary_images[{}]".format(idx) )
            
            try:
                ProductImage.objects.create( product = product, image = image_object )
            except IntegrityError:
                raise Exception( "The image with id provided in secondary_images[{}] is repeated".format(idx) )