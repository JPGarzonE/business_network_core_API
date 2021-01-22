# Serializers locations

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from ..models import SupplierLocation, SupplierSaleLocation
from multimedia.models import Image
from multimedia.serializers.images import ImageModelSerializer


class SupplierLocationModelSerializer(serializers.ModelSerializer):
    """Supplier Location model serializer."""

    image = ImageModelSerializer()

    class Meta:
        """Supplier Location Serializer meta class."""

        model = SupplierLocation

        fields = (
            'id',
            'supplier',
            'country',
            'city',
            'region',
            'address',
            'zip_code',
            'latitude',
            'longitude',
            'image',
        )

        read_only_fields = (
            'supplier',
            'image',
        )


class SupplierLocationNestedModelSerializer(serializers.ModelSerializer):
    """Supplier location nested model serializer."""

    class Meta:
        """Supplier Location Serializer meta class."""

        model = SupplierLocation

        fields = (
            'id',
            'country',
            'city',
            'region',
            'address',
            'zip_code',
            'latitude',
            'longitude'
        )


class SupplierSaleLocationModelSerializer(serializers.ModelSerializer):
    """Supplier Sale Location model serializer."""

    class Meta:
        """Supplier Sale Location meta class."""

        model = SupplierSaleLocation

        fields = (
            'id',
            'supplier',
            'country',
            'city',
            'region'
        )

        read_only_fields = (
            'supplier',
        )


class UpdateSupplierSummarySaleLocationSerializer(serializers.Serializer):
    """
    Supplier Sale Location serializer for updating supplier summary.
    The request 
    """

    id = serializers.IntegerField(
        required = False,
        allow_null = True
    )

    country = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )


class HandleSupplierLocationSerializer(serializers.ModelSerializer):
    """Create and update supplier location"""

    requires_context = True

    country = serializers.CharField(
        min_length = 2,
        max_length = 40
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    address = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    zip_code = serializers.CharField(
        min_length = 2,
        max_length = 10,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    latitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6,
        required = False
    )

    longitude = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6,
        required = False
    )

    image_id = serializers.IntegerField(required = False)

    principal = serializers.BooleanField( required = False,
        help_text = "Attribute to indicate if its the main location of a supplier")

    class Meta:
        """Supplier Location meta class."""

        model = SupplierLocation

        fields = (
            'country',
            'city',
            'region',
            'address',
            'zip_code',
            'latitude',
            'longitude',
            'image_id',
            'principal',
        )

    @transaction.atomic
    def create(self, data):
        """Create new supplier location."""
        supplier = self.context['supplier']
        
        principal = data.pop("principal") if data.get("principal") else not bool(supplier.principal_location)
        
        image = None
        if data.get('image_id'):
            image_id = data.pop("image_id")
            try:
                image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'image_id'")

        location = SupplierLocation.objects.create(
            supplier = supplier,
            **data
        )

        if principal is True:
            supplier.principal_location = location
            supplier.save()
        
        if image:
            location.image = image
            location.save()

        return location
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update a supplier location."""
        supplier = self.context['supplier']

        if validated_data.get('image_id'):
            image_id = validated_data.pop("image_id")
            try:
                image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                raise Exception("Theres no image with the id provided in 'image_id'")

            instance.image = image

        principal = validated_data.pop("principal") if validated_data.get("principal") else not bool(supplier.principal_location)

        updated_location = super().update(instance, validated_data)

        if principal is True:
            supplier.principal_location = updated_location
            supplier.save()

        return updated_location


class HandleSupplierSaleLocationSerializer(serializers.ModelSerializer):
    """Creates and update supplier sales location."""

    requires_context = True

    country = serializers.CharField(
        min_length = 2,
        max_length = 40
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    region = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    class Meta:
        """Supplier Sale Location meta class."""

        model = SupplierSaleLocation

        fields = (
            'country',
            'city',
            'region'
        )

    def create(self, data):
        """Create new supplier sale location."""
        supplier = self.context['supplier']

        location = SupplierSaleLocation.objects.create(
            supplier = supplier,
            **data
        )

        return location