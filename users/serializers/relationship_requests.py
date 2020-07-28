# users/serializers/relationship_requests.py

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from users.models import User, RelationshipRequest, Verification

# Serializers
from users.serializers.users import UserNestedModelSerializer
from companies.serializers.companies import CompanyModelSerializer
from users.serializers.verifications import VerificationModelSerializer

class RelationshipRequestModelSerializer(serializers.ModelSerializer):
    """Relationship request model serializer."""

    addressed = UserNestedModelSerializer()
    requester = UserNestedModelSerializer()

    class Meta:
        """Relationship request meta class."""

        model = RelationshipRequest

        fields = (
            'id',
            'requester',
            'addressed',
            'message',
            'blocked',
            'created_date',
            'last_updated'
        )

        read_only_fields = (
            'requester',
            'addressed',
        )


class CreateRelationshipRequestSerializer(serializers.Serializer):
    """Relationship request serializer.

        Handle relationship request creation
    """

    requires_context = True

    message = serializers.CharField(max_length=64, required = False)

    @transaction.atomic
    def create(self, data):
        """Create new user relationship request."""
        requester = self.context['requester']
        addressed = self.context['addressed']

        relationship_request = RelationshipRequest.objects.create(
            requester = requester,
            addressed = addressed,
            **data
        )

        return relationship_request