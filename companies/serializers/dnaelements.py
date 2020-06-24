"""Dnaelement serializer."""

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Dnaelement, Media
from multimedia.serializers.media import MediaModelSerializer

class DnaelementModelSerializer(serializers.ModelSerializer):
    """Dnaelement model serializer."""

    media = MediaModelSerializer()

    class Meta:
        """Dnaelement meta class."""

        model = Dnaelement

        fields = (
            'id',
            'company',
            'category',
            'name',
            'description',
            'media'
        )

        read_only_fields = (
            'company'
            'media',
        )



class HandleCompanyDnaelementSerializer(serializers.ModelSerializer):
    """Create and update a company Dnaelement"""

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
        required = False,
        allow_null = True,
        allow_blank = True
    )

    media_id = serializers.IntegerField(required = False)

    class Meta:
        """Dnaelement meta class."""

        model = Dnaelement

        fields = (
            'id',
            'category',
            'name',
            'description',
            'media_id'
        )

        read_only_fields = (
            'id',
            'company'
            'media_id',
        )

    @transaction.atomic
    def create(self, data):
        """Create new company Dnaelement."""
        company = self.context['company']
        media = None

        if( data.get('media_id') ):
            media_id = data.pop("media_id")
            media = Media.objects.get( id = media_id )

        dnaelement = Dnaelement.objects.create(
            company = company,
            **data
        )

        if media:
            dnaelement.media = media
            dnaelement.save()

        return dnaelement

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

        dna_updated = super().update(instance, validated_data)     

        return dna_updated