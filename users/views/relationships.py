"""User relationship views."""

# Django
from django.utils.decorators import method_decorator
from django.db.models import Q
 
# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from users.models import User, Relationship, Deal, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsAccountOwner, IsRelationOwner, UserIsVerified

# Serializers
from users.serializers import RelationshipModelSerializer, CreateRelationshipSerializer

# Errors
from django.db.utils import IntegrityError


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List User Relationships", tags = ["Relationships"],
    operation_description = "Endpoint to list all the relationships that have a user.",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'destroy', decorator = swagger_auto_schema( 
    operation_id = "Delete a Relationship", tags = ["Relationships"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete a relationship of a user.",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": 
        {"detail": "Invalid token."} } )}
))
@method_decorator( name = 'partial_update', decorator = swagger_auto_schema(
    operation_id = "Partial update a Relationship", tags = ["Relationships"],
    operation_description = "Endpoint to partial update a user relationship.", request_body = RelationshipModelSerializer,
    responses = { 200: RelationshipModelSerializer, 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
        400: openapi.Response("Bad request", examples = {"application/json":
            {"type": ["max_length 30 characters"]} 
        })
    }, security = [{ "api-key": [] }]
))
@method_decorator( name = 'update', decorator = swagger_auto_schema(auto_schema = None) )
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

        if self.action in ['partial_update', 'update', 'destroy']:
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


    @swagger_auto_schema( 
        operation_id = "Retrieve a Relationship", tags = ["Relationships"], security = [],
        operation_description = "Endpoint to retrieve a relationship of a user by its id.",
        responses = { 200: RelationshipModelSerializer, 404: openapi.Response("Not Found")}
    )
    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""

        response = super(RelationshipViewSet, self).retrieve(request, *args, **kwargs)

        data_status = status.HTTP_200_OK

        return Response( response.data, status = data_status )
