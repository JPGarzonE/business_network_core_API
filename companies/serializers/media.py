"""Media serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Media

class MediaModelSerializer(serializers.ModelSerializer):
    """Media model serializer."""

    name = serializers.CharField(
        min_length = 5,
        max_length = 60
    )

    type = serializers.CharField(
        min_length = 3,
        max_length = 10
    )

    class Meta:
        """Media meta class."""

        model = Media

        fields = (
            'id',
            'name',
            'type'
        )

        read_only_fields = (
            'id',
        )