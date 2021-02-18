# Serializer market showcases

# Django
from django.db import transaction
from django.db.utils import IntegrityError

# Django rest framework
from rest_framework import serializers

# Models
from market.models import ShowcaseProduct, ShowcaseSection

# Serializers
from multimedia.serializers import ImageModelSerializer

class ShowcaseProductModelSerializer(serializers.ModelSerializer):
    """Showcase product model serializer."""

    principal_image = ImageModelSerializer()

    class Meta:
        """Showcase product meta class."""

        model = ShowcaseProduct

        fields = (
            'id',
            'name',
            'tariff_heading',
            'description',
            'minimum_price',
            'maximum_price',
            'measurement_unit',
            'minimum_purchase',
            'principal_image',
            'supplier_name',
            'supplier_accountname',
            'product'
        )

class ShowcaseSectionModelSerializer(serializers.ModelSerializer):
    """Showcase section model serializer."""

    name = serializers.CharField(
        min_length = 1
    )

    section_elements = ShowcaseProductModelSerializer(
        source = "showcaseproduct_set",
        many = True
    )

    class Meta:
        """Showcase section meta class."""

        model = ShowcaseSection

        fields = (
            'id',
            'name',
            'section_elements'
        )


class ShowcaseSectionOverviewSerializer(serializers.Serializer):
    """Showcase section overview serializer."""

    name = serializers.CharField(min_length = 1)


class ShowcaseSerializer(serializers.Serializer):
    """Showcase Serializer."""

    sections = serializers.ListField(
        child = ShowcaseSectionModelSerializer()
    )