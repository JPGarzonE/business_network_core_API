# Serializers dnaelements

# Django
from django.db import transaction

# Django rest framework
from rest_framework import serializers

# Models
from ..models import DNAElement
from multimedia.models import Image
from multimedia.serializers.images import ImageModelSerializer


class DnaelementModelSerializer(serializers.ModelSerializer):
    """Dnaelement model serializer."""

    image = ImageModelSerializer()

    class Meta:
        """Dnaelement meta class."""

        model = DNAElement

        fields = (
            'id',
            'title',
            'category',
            'description',
            'image'
        )

        read_only_fields = (
            'image',
        )



class HandleSupplierDnaelementSerializer(serializers.ModelSerializer):
    """Create and update a supplier Dnaelement"""

    requires_context = True

    title = serializers.CharField(
        min_length = 2,
        max_length = 50,
        required = False,
        allow_null = True,
        allow_blank = True
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

    image_id = serializers.IntegerField(required = False)

    class Meta:
        """Dnaelement meta class."""

        model = DNAElement

        fields = (
            'id',
            'category',
            'title',
            'description',
            'image_id'
        )

        read_only_fields = (
            'id',
            'supplier',
            'image_id',
        )

    @transaction.atomic
    def create(self, data):
        """Create new supplier Dnaelement."""
        supplier = self.context['supplier']
        image = None

        if( data.get('image_id') ):
            image_id = data.pop("image_id")
            try:
                image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in 'image_id'" )

        dnaelement = DNAElement.objects.create(
            supplier = supplier,
            **data
        )

        if image:
            dnaelement.image = image
            dnaelement.save()

        return dnaelement

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        image = None

        if 'image_id' in validated_data :
            image_id = validated_data.pop('image_id')
            try:
                image = Image.objects.get( id = image_id )
            except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in 'image_id'" )
            
            if image:
                instance.image = image

        dna_updated = super().update(instance, validated_data)     

        return dna_updated