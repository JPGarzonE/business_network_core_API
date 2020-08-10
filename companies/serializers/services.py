"""Service serializer."""

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Service
from multimedia.models import Media
from multimedia.serializers.media import MediaModelSerializer

class ServiceModelSerializer(serializers.ModelSerializer):
    """Service model serializer."""

    media = MediaModelSerializer()

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
            'media'
        )

        read_only_fields = (
            'company'
            'media',
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

    media_id = serializers.IntegerField(required = False)

    class Meta:
        """Service meta class."""

        model = Service

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
        )

    @transaction.atomic
    def create(self, data):
        """Create new company service."""
        company = self.context['company']
        media = None

        if( data.get('media_id') ):
            media_id = data.pop("media_id")
            media = Media.objects.get( id = media_id )

        service = Service.objects.create(
            company = company,
            **data
        )

        if media:
            service.media = media
            service.save()

        return service

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

        service_updated = super().update(instance, validated_data)     

        return service_updated