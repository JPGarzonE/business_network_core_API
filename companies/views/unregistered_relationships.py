# companies/views/unregistered_relationships.py

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
from companies.models import Company, UnregisteredRelationship, UnregisteredCompany, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsUnregisteredRelationOwner

# Seralizers
from companies.serializers import (
    UnregisteredRelationshipModelSerializer, 
    CreateUnregisteredRelationshipSerializer,
    UpdateUnregisteredRelationshipSerializer
)

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
class UnregisteredRelationshipViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    """Unregistered Relationship view set."""

    queryset = UnregisteredRelationship.objects.all()
    serializer_class = UnregisteredRelationshipModelSerializer

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated, IsUnregisteredRelationOwner]

        return [permission() for permission in permissions]

    def get_object(self):
        """Return the unregistered relationship by the id"""
        unregistered_relationship = get_object_or_404(
            UnregisteredRelationship,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return unregistered_relationship

    @transaction.atomic
    def perform_destroy(self, instance):
        """Disable unregistered relationship."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()
    
    def reborn_entity(self, instance):
        """Enable unregistered relationship previously deleted"""
        instance.visibility = VisibilityState.OPEN.value
        instance.save()

        return instance

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
        self.company = Company.objects.get( user = request.user )

        try:
            unregistered_relationship_serializer = CreateUnregisteredRelationshipSerializer(
                data = request.data,
                context = {"requester": self.company}
            )

            unregistered_relationship_serializer.is_valid(raise_exception = True)
            try:
                unregistered_relationship = unregistered_relationship_serializer.save()
                data = self.get_serializer(unregistered_relationship).data
                data_status = status.HTTP_201_CREATED
            except IntegrityError as e:
                unregistered = UnregisteredCompany.objects.get( id = request.data.get("unregistered_id") )
                reborn_relationship = UnregisteredRelationship.objects.get(
                    requester = self.company,
                    unregistered = unregistered
                )

                if reborn_relationship.visibility == VisibilityState.DELETED:

                    reborn_result = self.reborn_entity(reborn_relationship)
                    data = self.get_serializer(reborn_result).data
                    data_status = status.HTTP_201_CREATED
                else:
                    data = {"detail": "This relationship alredy exists"}
                    data_status = status.HTTP_400_BAD_REQUEST

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


@method_decorator( name = 'get', decorator = swagger_auto_schema( operation_id = "List unregistered relationships", tags = ["Unregistered Relationships"], 
    operation_description = "Endpoint to list all the unregistered relationships of a company",
    responses = { 404: openapi.Response("Not Found") }, security = []
) )
class ListUnregisteredRelationships(ListAPIView):
    """API view to list all Unregistered Relationships of a user"""

    serializer_class = UnregisteredRelationshipModelSerializer

    def get_queryset(self):
        """Return company unregistered relationship objects"""
        return UnregisteredRelationship.objects.filter(
            requester = self.company,
            visibility = VisibilityState.OPEN.value
        )
    
    def list(self, request, *args, **kwargs):
        """Handle the list event."""   
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(ListUnregisteredRelationships, self).list(request, *args, **kwargs)
        
    

