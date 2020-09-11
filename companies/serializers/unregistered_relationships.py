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

    unregistered_id = serializers.IntegerField(
        help_text = "Id of an unregistered company that alredy exists in the platform",
        required = False
    )

    unregistered = UnregisteredCompanyModelSerializer(
        help_text = "Data of the unregistered company that is going to be created",
        required = False
    )

    type = serializers.CharField(
        help_text = "Type of the unregistered relationship. Ej: Comprador, Socio, Aliado estratégico",
        min_length = 1,
        max_length = 30
    )

    @transaction.atomic
    def create(self, data):
        """Create a new unregistered relationship"""
        requester = self.context['requester']
        type = data['type']

        if 'unregistered_id' in data:
            if 'unregistered' in data:
                raise Exception("You can pass the unregistered_id or the unregistered object. Not both at the same time.")

            unregistered_id = data['unregistered_id']
            
            try:
                unregistered = UnregisteredCompany.objects.get(id = unregistered_id)
            except UnregisteredCompany.DoesNotExist:
                raise Exception("There's no unregistered company with the id in 'unregistered_id'")

        elif 'unregistered' in data:
            unregistered_data = data.pop("unregistered")

            unregistered = UnregisteredCompany.objects.create(**unregistered_data)
        else:
            raise Exception("It's needed either one of both 'unregistered_id' or 'unregistered'")

        unregistered_relationship = UnregisteredRelationship.objects.create(
            requester = requester,
            unregistered = unregistered,
            type = type
        )

        return unregistered_relationship


class UpdateUnregisteredRelationshipSerializer(serializers.ModelSerializer):
    """Update an unregistered relationship"""

    type = serializers.CharField(
        help_text = "Type of the unregistered relationship. Ej: Comprador, Socio, Aliado estratégico",
        min_length = 1,
        max_length = 30
    )

    class Meta:
        """Unregistered relationship meta class."""

        model = UnregisteredRelationship

        fields = ('id', 'type')