"""Company locations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Django
from django.conf import settings
from django.utils.decorators import method_decorator

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company, CompanyLocation, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import CompanyLocationModelSerializer, HandleCompanyLocationSerializer

# Utils
from distutils.util import strtobool

@method_decorator(name='list', decorator = swagger_auto_schema( operation_id = "List company operative locations", tags = ["Locations"],
    operation_description = "Endpoint to list all the locations where a company operates." ,
    manual_parameters = [ openapi.Parameter(name = "principal", default = False, in_ = openapi.IN_QUERY, type = "Boolean",
    description = "Filter the locations depending if they are principal or secondary locations. If its true, return the main location of the company") ], 
    responses = { 404: openapi.Response("Not Found") }, security = [{ "Anonymous": [] }]
))
class CompanyLocationViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Company Location view set"""

    serializer_class = CompanyLocationModelSerializer
    company = None
    principal_location = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(CompanyLocationViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['retrieve']:
            permissions = [IsAuthenticated]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return company locations"""
        principal = self.principal_location if self.principal_location else None
        principal_location_id = self.company.principal_location.id if self.company.principal_location else None

        if principal is True:
            return CompanyLocation.objects.filter(
                id = principal_location_id
            )

        elif principal is False:
            return CompanyLocation.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value
            ).exclude( id = principal_location_id )
        else:
            return CompanyLocation.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value
            )


    def list(self, request, *args, **kwargs):
        """Valid param principal before super list eventually executes get_queryset method"""
        principal = self.request.query_params.get('principal')

        if principal:
            try:
                self.principal_location = bool( strtobool(principal) )
            except ValueError:
                data = {"detail": "Query param 'principal' must be a boolean value"}
                return Response(data, status = status.HTTP_400_BAD_REQUEST)

        return super(CompanyLocationViewSet, self).list(request, *args, **kwargs)


    def get_object(self):
        """Return the location by the id"""
        location = get_object_or_404(
            CompanyLocation,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return location

    def perform_destroy(self, instance):
        """Disable location."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    @swagger_auto_schema( operation_id = "Partial update location", tags = ["Locations"], request_body = CompanyLocationModelSerializer,
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} 
            })
        }, security = [{ "api_key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Endpoint to update partially a location object. It is partial, so its not needed pass all the body values"""
        try:
            instance = self.get_object()
            serializer = HandleCompanyLocationSerializer(
                instance = instance,
                data=  request.data,
                context = {'company': self.company},
                partial = True
            )
            serializer.is_valid(raise_exception=True)
            location = serializer.save()

            data = self.get_serializer(location).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status = data_status)

    @swagger_auto_schema( operation_id = "Create a location", tags = ["Locations"], request_body = HandleCompanyLocationSerializer,
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Authentication credentials were not provided"} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} 
            })
        }, security = [{ "api_key": [] }])
    def create(self, request, *args, **kwargs):
        """Endpoint to create a location of a company."""
        try:
            location_serializer = HandleCompanyLocationSerializer(
                data = request.data,
                context = {'company': self.company}
            )
            location_serializer.is_valid(raise_exception = True)
            location = location_serializer.save()

            data = self.get_serializer(location).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( operation_id = "Retrieve a location", tags = ["Locations"],
        responses = { 404: openapi.Response("Not Found")}, security = [{ "api_key": [] }])
    def retrieve(self, request, *args, **kwargs):
        """Endpoint to retrieve a location by its id"""
        response = super(CompanyLocationViewSet, self).retrieve(request, *args, **kwargs)

        data = response.data
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
