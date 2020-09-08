# companies/serializers/unregistered_reltionships.py

# Django rest framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Django
from django.db import transaction

# Models
from companies.models import UnregisteredRelationship, UnregisteredCompany

# Serializers
from companies.serializers import UnregisteredCompanyModelSerializer

class UnregisteredRelationshipModelSerializer(serializers.ModelSerializer):
    """Unregistered Relationship model serializer."""

    unregistered = UnregisteredCompanyModelSerializer()

    class Meta:
        """Unregistered relationship meta class."""

        model = UnregisteredRelationship

        fields = ('id', 'requester', 'unregistered', 'type')

        read_only_fields = ('id', 'requester', 'unregistered')


class CreateUnregisteredRelationshipSerializer(serializers.Serializer):
    """Handle unregistered relationship creation."""

    requires_context = True

    unregistered_id = serializers.IntegerField()

    type = serializers.CharField(
        help_text = "Type of the unregistered relationship. Ej: Comprador, Socio, Aliado estratégico",
        min_length = 1,
        max_length = 30
    )

    @transaction.atomic
    def create(self, data):
        """Create a new unregistered relationship"""
        requester = self.context['requester']
        unregistered_id = data['unregistered_id']
        type = data['type']
        
        unregistered = get_object_or_404(
            UnregisteredCompany,
            id = unregistered_id
        )

        unregistered_relationship = UnregisteredRelationship.objects.create(
            requester = requester,
            unregistered = unregistered,
            type = type
        )

        return unregistered_relationship

