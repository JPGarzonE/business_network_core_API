# Views relationship_requests

# Django
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Q
 
# Django REST framework
from rest_framework import mixins, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import Company, Relationship, RelationshipRequest

# Permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from ..permissions import IsCompanyMemberWithEditPermission

# Serializers
from ..serializers import (
    RelationshipRequestModelSerializer, 
    CreateRelationshipRequestSerializer, 
    RelationshipModelSerializer, 
    CreateRelationshipSerializer
)

# Errors
from django.db.utils import IntegrityError


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List the relationship requests sent", tags = ["Relationship Requests"],
    operation_description = """Endpoint to list all the relationship requests that have 
        been sent by the company with the accountname by param.""",
    responses = { 404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
))
@method_decorator( name = 'destroy', decorator = swagger_auto_schema(
    operation_id = "Delete a relationship request sent", tags = ["Relationship Requests"],
    operation_description = """Endpoint to delete a relationship request that have
        been sent by the company with the accountname by param.""",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }, 
    security = [{ "api-key": ["Requester company has to be the relation requester"] }]
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema(
    operation_id = "Retrieve a relationship request sent", tags = ["Relationship Requests"], security = [{ "api-key": [] }],
    operation_description = """Endpoint to retrieve a relationship request that have 
        been sent by the company with the accountname by param.""",
    responses = { 200: RelationshipRequestModelSerializer, 404: openapi.Response("Not Found")}
))
class SentRelationshipRequestViewSet(mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """Relationship request viewset that was sent by the company with the accountname by param"""

    serializer_class = RelationshipRequestModelSerializer
    requester_company = None

    def dispatch(self, request, *args, **kwargs):
        accountname = kwargs['accountname']
        self.requester_company = get_object_or_404(Company, accountname = accountname)

        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return relationship requests sent by the request company."""
        relationship_requests = RelationshipRequest.objects.filter(
            requester = self.requester_company
        )

        return relationship_requests


    def get_data_owner_company(self):
        """Return the company owner of the data (Requester of the Relationship request)"""
        return self.requester_company


    def get_object(self):
        """Return the sent relationship request by the id"""
        
        return get_object_or_404(
            RelationshipRequest,
            id = self.kwargs['pk'],
            requester = self.requester_company
        )


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List the relationship requests recieved", tags = ["Relationship Requests"],
    operation_description = """Endpoint to list all the relationship requests 
        recieved by the company with the accountname by param.""",
    responses = { 404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema(
    operation_id = "Retrieve a relationship request recieved", tags = ["Relationship Requests"], security = [{ "api-key": [] }],
    operation_description = """Endpoint to retrieve a relationship request recieved by 
        the company with the accountname by param""",
    responses = { 200: RelationshipRequestModelSerializer, 404: openapi.Response("Not Found")}
))
@method_decorator( name = 'update', decorator = swagger_auto_schema(auto_schema = None) )
class RecievedRelationshipRequestViewSet(mixins.ListModelMixin,
                                    mixins.UpdateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """Relationship request viewset that was recieved by the company with the accountname by param"""

    serializer_class = RelationshipRequestModelSerializer
    addressed_company = None

    def dispatch(self, request, *args, **kwargs):
        accountname = kwargs['accountname']
        self.addressed_company = get_object_or_404(Company, accountname = accountname)

        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return user relationship requests recieved 
        by the company with the accountname by param"""

        blocked = self.request.query_params.get('blocked')
        blocked = self.str_to_bool(blocked) if blocked else None

        if type(blocked) is bool:
            relationship_requests = RelationshipRequest.objects.filter(
                addressed = self.addressed_company,
                blocked = blocked
            )
        else:
            relationship_requests = RelationshipRequest.objects.filter(
                addressed = self.addressed_company
            )

        return relationship_requests

    def str_to_bool(self, str):
        if str.lower() == "false":
            return False
        elif str.lower() == "true":
            return True
        
        return None


    def get_data_owner_company(self):
        """Return the company owner of the data (Addressed of the Relationship request)"""
        return self.addressed_company


    def get_object(self):
        """Return the recieved relationship request by the id"""
        relationship_request = get_object_or_404(
            RelationshipRequest,
            id = self.kwargs['pk'],
            addressed = self.addressed_company
        )

        return relationship_request


    @swagger_auto_schema( tags = ["Relationship Requests"], request_body = CreateRelationshipSerializer,
        security = [{ "api-key": ["Relation addressed needed"] }],
        manual_parameters = [
            openapi.Parameter(name = "action", in_ = openapi.IN_QUERY, type = "String", required = True,
                enum = ["accept", "deny"],
                description = """
                    Action that is going to be executed over the relationship request.\n
                    This param has only the two possible values in enum.\n""")
        ],
        responses = { 200: RelationshipRequestModelSerializer, 201: RelationshipModelSerializer,
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "the action param have to be accept or deny"} }), 
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            404: openapi.Response("Not Found"),
            409: openapi.Response("Conflict", examples = {"application/json": 
                {"detail": "Error. This relationship alredy exist."} })
        })
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Accept or deny a Relationship Request\n
            Endpoint to accept or deny a relationship request. 
            This actions is executed depending the value on the accept query param.\n
            - The response return `200` if the relationship request was denied succesfully.\n
            - The response return `201` if the relationship request was accepted succesfully. 
            In consecuence a relationship is created.\n
            *This endpoint can only be used by the relation addressed company.*
        """

        action = request.query_params.get('action')

        if action:
            instance = self.get_object()

            if action == "accept":
                return self.accept(
                    relationship_type = request.data.get("type"),
                    relationship_request = instance
                )
            elif action == "deny":
                return self.deny(relationship_request = instance)
            else:
                return Response( 
                    {"detail": "the action param have to be accept or deny"}, 
                    status = status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response( {"detail": "the update need the <<action>> query param"}, 
                status = status.HTTP_400_BAD_REQUEST)


    @transaction.atomic
    def accept(self, relationship_type, relationship_request):
        """Accept the relationship_request.
        Delete the relationship_request and create a relationship."""
        
        relationship_serializer = CreateRelationshipSerializer(
            data = {"type": relationship_type} if relationship_type else {},
            context = {'requester': relationship_request.requester, 'addressed': relationship_request.addressed}
        )

        relationship_serializer.is_valid(raise_exception = True)

        try:
            relationship = relationship_serializer.save()
            data = RelationshipModelSerializer(relationship).data
            data_status = status.HTTP_201_CREATED
            
            relationship_request.delete()
        except IntegrityError:
            data = {
                'detail': 'Error. This relationship alredy exist.'
            }
            data_status = status.HTTP_409_CONFLICT
        
        return Response(data, status = data_status)


    @transaction.atomic
    def deny(self, relationship_request):
        """Deny the relationship_request"""
        relationship_request_serializer = RelationshipRequestModelSerializer(
            instance = relationship_request,
            data = {"blocked": True},
            partial = True
        )
        relationship_request_serializer.is_valid(raise_exception = True)
        relationship_res = relationship_request_serializer.save()

        data = self.get_serializer(relationship_res).data

        return Response(data, status.HTTP_200_OK)

    

class RelationshipRequestViewSet(mixins.CreateModelMixin,
                                viewsets.GenericViewSet):
    """Relationship request viewset to send a relationship request to a target_company"""

    serializer_class = RelationshipRequestModelSerializer
    target_user = None
    requester_company = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that both company exists"""
        target_company_accountname = kwargs['target_company_accountname']
        requester_company_accountname = kwargs['requester_company_accountname']
        self.target_company = get_object_or_404(Company, accountname = target_company_accountname)
        self.requester_company = get_object_or_404(Company, accountname = requester_company_accountname)

        return super(RelationshipRequestViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]
        else:
            permissions = [IsAdminUser]

        return [permission() for permission in permissions]


    def get_data_owner_company(self):
        """Return the company owner of the data (Requester of the Relationship request)"""
        return self.addressed_company


    @swagger_auto_schema( tags = ["Relationship Requests"], request_body = CreateRelationshipRequestSerializer,
        responses = { 200: RelationshipRequestModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            409: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "The relationship alredy have a pending request."} })
        }, security = [{ "api-key": [] }]
    )
    def create(self, request, *args, **kwargs):
        """Send a relationship request\n
            Endpoint to send (create) a relationship request to an addressed company (`target company`).
        """

        relationship_request_validation = RelationshipRequest.objects.filter(
            ( Q(requester = self.requester_company) & Q(addressed = self.target_company) ) 
            | ( Q(requester = self.target_company) & Q(addressed = self.requester_company) )
        )
        relationship_validation = Relationship.objects.filter(
            ( Q(requester = self.requester_company) & Q(addressed = self.target_company) ) 
            | ( Q(requester = self.target_company) & Q(addressed = self.requester_company) )
        )

        if relationship_request_validation:
            return Response({"detail": "The relationship alredy have a pending request"}, status.HTTP_409_CONFLICT)
        elif  relationship_validation:
            return Response({"detail": "The relationship alredy exists"}, status.HTTP_409_CONFLICT)

        relationship_request_serializer = CreateRelationshipRequestSerializer(
            data = request.data,
            context = {'requester': self.requester_company, 'addressed': self.target_company}
        )

        relationship_request_serializer.is_valid(raise_exception = True)
        relationship_request = relationship_request_serializer.save()

        data = self.get_serializer(relationship_request).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)