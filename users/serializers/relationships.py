# users/serializers/relationships/py

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from users.models import User, Relationship, Verification

# Serializers
from users.serializers.users import UserNestedModelSerializer
from companies.serializers.companies import CompanyModelSerializer
from users.serializers.verifications import VerificationModelSerializer

class RelationshipModelSerializer(serializers.ModelSerializer):
    """Relationship model serializer."""

    addressed = UserNestedModelSerializer()
    requester = UserNestedModelSerializer()

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
    """User create relation serializer.

        Handle relationship creation
    """

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
        
        if not requester.is_active or not addressed.is_active:
            raise Exception("Requester and addressed both have to be active users")

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