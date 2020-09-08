"""Service serializer."""

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Service
from multimedia.models import Image
from multimedia.serializers.images import ImageModelSerializer

class ServiceModelSerializer(serializers.ModelSerializer):
    """Service model serializer."""

    images = ImageModelSerializer()

    class Meta:
        """Service meta class."""

        model = Service

        fields = (
            'id',
            'company',
            'category',
            'name',
            'price',
            'description',
            'images'
        )

        read_only_fields = (
            'company',
            'images',
        )



class HandleCompanyServiceSerializer(serializers.ModelSerializer):
    """Create and update a company service"""

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
        min_length = 2,
        max_length = 20,
        required = False,
        allow_null = True
    )

    images = serializers.ListField(
        child = serializers.IntegerField(),
        required = False,
        help_text = "Array with the ids of the images (previously uploaded)"
    )

    class Meta:
        """Service meta class."""

        model = Service

        fields = (
            'id',
            'category',
            'name',
            'price',
            'description',
            'images'
        )

        read_only_fields = (
            'id',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company service."""
        company = self.context['company']

        service = Service.objects.create(
            company = company,
            **data
        )

        if 'images' in data:
            images = data.pop("images")

            for image_id in images:
                service.images.add( image_id )

        return service

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        if 'images' in validated_data:
            images = validated_data.pop("images")

            for image_id in images:
                instance.images.add( image_id )

        service_updated = super().update(instance, validated_data)     

        return service_updated