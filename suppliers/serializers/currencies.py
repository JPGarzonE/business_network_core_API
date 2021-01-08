# Serializers currencies

# Django
from django.db import transaction
from django.db.utils import IntegrityError

# Django rest framework
from rest_framework import serializers

# Models
from ..models import Currency


class CurrencyModelSerializer(serializers.ModelSerializer):
    """Currency model serializer."""

    class Meta:
        """Currency meta class."""

        model = Currency

        fields = (
            'id',
            'name',
            'code',
            'region',
        )