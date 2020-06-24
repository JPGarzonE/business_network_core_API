"""User relations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

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
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Relationship view set"""

    serializer_class = RelationshipModelSerializer

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
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsAccountOwner, UserIsVerified]
        else:
            permissions = [IsAuthenticated, IsAccountOwner, IsRelationOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company relationships"""
        if self.request.query_params.get('addressed_id'):
            relationship = Relationship.objects.filter(
                requester = self.user,
                addressed = self.request.query_params.get('addressed_id'),
                visibility = VisibilityState.OPEN
            )

            return relationship

        else:
            requester_relationships = Relationship.objects.filter(
                requester = self.user,
                visibility = VisibilityState.OPEN
            )

            addressed_relationships = Relationship.objects.filter(
                addressed = self.user,
                visibility = VisibilityState.OPEN
            )

            return requester_relationships | addressed_relationships

    def get_object(self):
        """Return the relationship by the id"""
        relationship = get_object_or_404(
            Relationship,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN
        )

        return relationship

    def perform_destroy(self, instance):
        """Disable product."""
        instance.visibility = VisibilityState.DELETED
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Relationship creation."""
        relationship_serializer = CreateRelationshipSerializer(
            data = request.data,
            context = {'requester': self.user}
        )

        relationship_serializer.is_valid(raise_exception = True)
        try:
            relationship = relationship_serializer.save()
            data = self.get_serializer(relationship).data
            data_status = status.HTTP_201_CREATED
        except IntegrityError:
            data = {
                'detail': 'Error. This relationship alredy exist.'
            }
            data_status = status.HTTP_409_CONFLICT
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(RelationshipViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'relationship': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
