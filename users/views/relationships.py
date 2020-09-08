"""User relationship views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Django
from django.db.models import Q

# Models
from users.models import User, Relationship, Deal, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsAccountOwner, IsRelationOwner, UserIsVerified

# Serializers
from users.serializers import RelationshipModelSerializer, CreateRelationshipSerializer

# Errors
from django.db.utils import IntegrityError

class RelationshipViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Relationship view set"""

    serializer_class = RelationshipModelSerializer
    user = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the user exists"""
        user_id = kwargs['user_pk']
        self.user = get_object_or_404(User, id = user_id)

        return super(RelationshipViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.user

    def get_permissions(self):
        """Assign permission based on action"""
        print("action")
        print(self.action)
        if self.action in ['update', 'destroy']:
            permissions = [IsAuthenticated, IsAccountOwner, IsRelationOwner]
        else:
            permissions = [AllowAny]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return user relationships"""
        if self.request.query_params.get('addressed_id'):
            relationship = Relationship.objects.filter(
                requester = self.user,
                addressed = self.request.query_params.get('addressed_id'),
                visibility = VisibilityState.OPEN.value
            )

            return relationship

        else:
            relationships = Relationship.objects.filter(
                (Q(requester = self.user) | Q(addressed = self.user)) & Q(visibility = VisibilityState.OPEN.value)
            )

            return relationships

    def get_object(self):
        """Return the relationship by the id"""
        relationship = get_object_or_404(
            Relationship,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return relationship

    def perform_destroy(self, instance):
        """Disable product."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(RelationshipViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'relationship': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
