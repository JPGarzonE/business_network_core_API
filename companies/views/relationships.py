# Views relationships

# Constants
from ..constants import VisibilityState

# Django
from django.utils.decorators import method_decorator
from django.db.models import Q
 
# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import Company, Relationship

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsCompanyMemberWithEditPermission

# Serializers
from ..serializers import RelationshipModelSerializer

# Errors
from django.db.utils import IntegrityError


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List Company Relationships", tags = ["Relationships"],
    operation_description = "Endpoint to list all the relationships that have a company.",
    manual_parameters = [
        openapi.Parameter(name = "addressed_id", in_ = openapi.IN_QUERY, type = "int"),
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'destroy', decorator = swagger_auto_schema( 
    operation_id = "Delete a Relationship", tags = ["Relationships"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete a relationship of a company.",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": 
        {"detail": "Invalid token."} } )}
))
@method_decorator( name = 'partial_update', decorator = swagger_auto_schema(
    operation_id = "Partial update a Relationship", tags = ["Relationships"],
    operation_description = "Endpoint to partial update a company relationship.", request_body = RelationshipModelSerializer,
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
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        accountname = kwargs['accountname']
        self.company = get_object_or_404(Company, accountname = accountname)

        return super(RelationshipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""

        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return company relationships"""

        if self.request.query_params.get('addressed_id'):
            relationship = Relationship.objects.filter(
                requester = self.company,
                addressed = self.request.query_params.get('addressed_id'),
                visibility = VisibilityState.OPEN.value
            )

            return relationship

        else:
            relationships = Relationship.objects.filter(
                (Q(requester = self.company) | Q(addressed = self.company)) & Q(visibility = VisibilityState.OPEN.value)
            )

            return relationships


    def get_data_owner_company(self):
        """Return the company owner of the data"""
        return self.company


    def get_object(self):
        """Return the relationship by its id"""
        relationship = get_object_or_404(
            Relationship,
            (Q(requester = self.company) | Q(addressed = self.company)),
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return relationship

    def perform_destroy(self, instance):
        """Disable relationship."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()


    @swagger_auto_schema( 
        operation_id = "Retrieve a Relationship", tags = ["Relationships"], security = [],
        operation_description = "Endpoint to retrieve a relationship of a company by its id.",
        responses = { 200: RelationshipModelSerializer, 404: openapi.Response("Not Found")}
    )
    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""

        response = super(RelationshipViewSet, self).retrieve(request, *args, **kwargs)

        data_status = status.HTTP_200_OK

        return Response( response.data, status = data_status )
