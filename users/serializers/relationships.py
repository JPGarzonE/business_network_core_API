"""Products serializer."""

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

    verification = VerificationModelSerializer()
    addressed = UserNestedModelSerializer()
    requester = UserNestedModelSerializer()

    class Meta:
        """Relationship meta class."""

        model = Relationship

        fields = (
            'id',
            'requester',
            'addressed',
            'type',
            'verification'
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

    addressed_id = serializers.CharField(
        min_length = 1,
        max_length = 50
    )

    type = serializers.CharField(
        min_length = 1,
        max_length = 30
    )

    @transaction.atomic
    def create(self, data):
        """Create new user relationship."""
        requester = self.context['requester']
        addressed_id = data['addressed_id']
        type = data["type"]

        addressed = User.objects.filter(
            id = addressed_id,
            is_active = True
        )
        verification = Verification.objects.create( verified = False, state = "None" )

        relationship = Relationship.objects.create(
            requester = requester,
            addressed = addressed[0],
            type = type,
            verification = verification
        )

        return relationship