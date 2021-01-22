# users/serializers/relationships/py

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from ..models import Relationship

# Serializers
from .companies import CompanyModelSerializer


class RelationshipModelSerializer(serializers.ModelSerializer):
    """Relationship model serializer."""

    addressed = CompanyModelSerializer()
    requester = CompanyModelSerializer()

    type = serializers.CharField(
        min_length = 1,
        max_length = 30,
        required = False
    )

    class Meta:
        """Relationship meta class."""

        model = Relationship

        fields = (
            'id',
            'requester',
            'addressed',
            'type'
        )

        read_only_fields = (
            'requester',
            'addressed',
        )



class CreateRelationshipSerializer(serializers.Serializer):
    """Handle relationship creation"""

    requires_context = True

    type = serializers.CharField(
        min_length = 1,
        max_length = 30,
        required = False
    )

    @transaction.atomic
    def create(self, data):
        """Create new user relationship."""
        requester = self.context['requester']
        addressed = self.context['addressed']

        type = data.get("type")

        if type:
            relationship = Relationship.objects.create(
                requester = requester,
                addressed = addressed,
                type = type
            )
        else:
            relationship = Relationship.objects.create(
                requester = requester,
                addressed = addressed
            )

        return relationship