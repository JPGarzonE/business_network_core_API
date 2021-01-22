# Models unregistered_relationships

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.db import transaction
from django.utils.decorators import method_decorator

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Errors
from django.db.utils import IntegrityError

# Models
from ..models import Company, UnregisteredRelationship, UnregisteredCompany

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsCompanyMemberWithEditPermission

# Seralizers
from ..serializers import (
    UnregisteredRelationshipModelSerializer, 
    CreateUnregisteredRelationshipSerializer,
    UpdateUnregisteredRelationshipSerializer
)


@method_decorator( name = 'list', decorator = swagger_auto_schema( 
    operation_id = "List unregistered relationships", tags = ["Unregistered Relationships"], 
    operation_description = "Endpoint to list all the unregistered relationships of a company",
    responses = { 404: openapi.Response("Not Found") }, security = []
) )
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve an unregistered relationship", tags = ["Unregistered Relationships"],
    operation_description = "Endpoint to retrieve an unregistered relationship by its id",
    responses = { 200: UnregisteredRelationshipModelSerializer, 404: openapi.Response("Not Found")}, 
    security = []
))
@method_decorator( name = 'update', decorator = swagger_auto_schema( auto_schema = None ) )
@method_decorator( name = 'destroy', decorator = swagger_auto_schema( operation_id = "Delete an unregistered relationship",
         tags = ["Unregistered Relationships"],
        operation_description = "Endpoint to delete an unregistered relationship by its id",
        responses = { 204: "No Content", 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
        }, security = [{ "api-key": [] }]
))
class UnregisteredRelationshipViewSet(mixins.ListModelMixin,
                                    mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    """Unregistered Relationship view set."""

    serializer_class = UnregisteredRelationshipModelSerializer
    requester_company = None

    def dispatch(self, request, *args, **kwargs):
        requester_company_accountname = kwargs['requester_company_accountname']
        self.requester_company = get_object_or_404(Company, accountname = requester_company_accountname)

        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]

        return [permission() for permission in permissions]

    
    def get_data_owner_company(self):
        """Return the company owner of the data 
        (Requester of the Unregistered Relationship)"""

        return self.requester_company
 

    def get_object(self):
        """Return the unregistered relationship by the id"""

        return get_object_or_404(
            UnregisteredRelationship,
            id = self.kwargs['pk'],
            requester = self.requester_company
        )

    def get_queryset(self):
        """Return company unregistered relationships"""

        return UnregisteredRelationship.objects.filter(
            requester = self.requester_company
        )

    @swagger_auto_schema( tags = ["Unregistered Relationships"], request_body = CreateUnregisteredRelationshipSerializer,
        responses = { 200: UnregisteredRelationshipModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "You can pass the unregistered_id or the unregistered object. Not both at the same time."}
            })
        }, security = [{ "api-key": [] }])
    def create(self, request, *args, **kwargs):
        """Create an unregistered relationship\n
        Endpoint that creates an unregistered relationship.\n 
        It create it passing the id of an unregistered company that alredy exists in the platform.\n
        Or with the data of the company for creating a new unregistered company.
        """

        try:
            unregistered_relationship_serializer = CreateUnregisteredRelationshipSerializer(
                data = request.data,
                context = {"requester": self.requester_company}
            )

            unregistered_relationship_serializer.is_valid(raise_exception = True)
            unregistered_relationship = unregistered_relationship_serializer.save()
            
            data = self.get_serializer(unregistered_relationship).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {
                'detail': str(e)
            }
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Unregistered Relationships"], request_body = UpdateUnregisteredRelationshipSerializer,
        responses = { 200: UnregisteredRelationshipModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"type": ["This field may not be null"]}
            })
        }, security = [{ "api-key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Update partially an unregistered relationship.\n
        It can only update the type of the unregistered relationhsip.\n
        Theres no possibility to modify an unregistered company that alredy exists.
        """
        try:
            instance = self.get_object()
            unregistered_relationship_serializer = UpdateUnregisteredRelationshipSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            unregistered_relationship_serializer.is_valid(raise_exception = True)
            unregistered_relationship = unregistered_relationship_serializer.save()

            data = self.get_serializer(unregistered_relationship).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)