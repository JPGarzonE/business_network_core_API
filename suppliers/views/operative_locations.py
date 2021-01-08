# Views operative_locations

# Constants
from companies.constants import VisibilityState

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
from ..models import SupplierProfile, SupplierLocation

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission

# Serializers
from ..serializers import SupplierLocationModelSerializer, HandleSupplierLocationSerializer

# Utils
from distutils.util import strtobool


@method_decorator(name = 'destroy', decorator = swagger_auto_schema(
    operation_id = "Delete an operative location", tags = ["Supplier Locations"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete an operative location of a supplier by company accountname and location id.",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }
))
@method_decorator(name = 'update', decorator = swagger_auto_schema(auto_schema = None))
class SupplierLocationViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Supplier Location view set"""

    serializer_class = SupplierLocationModelSerializer
    supplier = None
    principal_param = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the supplier exists"""
        accountname = kwargs['accountname']
        self.supplier = get_object_or_404(
            SupplierProfile, company__accountname = accountname,
            visibility = VisibilityState.OPEN.value
        )

        return super(SupplierLocationViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.supplier

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsSupplierMemberWithEditPermission]

        return [permission() for permission in permissions]


    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the supplier)"""
        return self.supplier.company


    def get_queryset(self):
        """Return supplier locations"""
        principal = self.principal_param if self.principal_param else None

        if principal is True:
            return self.supplier.principal_location

        elif principal is False:
            principal_location_id = self.supplier.principal_location.id if self.supplier.principal_location else None

            return SupplierLocation.objects.filter(
                supplier = self.supplier,
                visibility = VisibilityState.OPEN.value
            ).exclude( id = principal_location_id )
        else:
            return SupplierLocation.objects.filter(
                supplier = self.supplier,
                visibility = VisibilityState.OPEN.value
            )


    @swagger_auto_schema( operation_id = "List supplier operative locations", tags = ["Supplier Locations"],
        operation_description = "Endpoint to list all the locations where a supplier operates." ,
        manual_parameters = [
            openapi.Parameter(name = "principal", default = False, in_ = openapi.IN_QUERY, type = "Boolean",
                description = """Filter the locations depending if they are principal or secondary locations. 
                If its true, return the main location of the supplier""")
        ],
        responses = { 404: openapi.Response("Not Found") }, security = []
    )
    def list(self, request, *args, **kwargs):
        """Valid param principal before super list eventually executes get_queryset method"""

        principal = self.request.query_params.get('principal')

        if principal:
            try:
                self.principal_param = bool( strtobool(principal) )
            except ValueError:
                data = {"detail": "Query param 'principal' must be a boolean value"}
                return Response(data, status = status.HTTP_400_BAD_REQUEST)

        return super(SupplierLocationViewSet, self).list(request, *args, **kwargs)


    def get_object(self):
        """Return the location by the id"""
        location = get_object_or_404(
            SupplierLocation,
            id = self.kwargs['pk'],
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

        return location

    def perform_destroy(self, instance):
        """Disable location."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()


    @swagger_auto_schema( operation_id = "Partial update operative location", tags = ["Supplier Locations"], 
        request_body = SupplierLocationModelSerializer, security = [{ "api-key": [] }],
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} 
            })
        })
    def partial_update(self, request, *args, **kwargs):
        """Endpoint to update partially a location where a supplier operates. 
            It is partial, so its not needed pass all the body values
        """

        try:
            instance = self.get_object()
            serializer = HandleSupplierLocationSerializer(
                instance = instance,
                data=  request.data,
                context = {'supplier': self.supplier},
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


    @swagger_auto_schema( operation_id = "Create operative location", tags = ["Supplier Locations"], 
        request_body = HandleSupplierLocationSerializer, security = [{ "api-key": [] }],
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": 
                {"detail": "Authentication credentials were not provided"} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} })
        })
    def create(self, request, *args, **kwargs):
        """Endpoint to create a location where a supplier operates."""

        try:
            location_serializer = HandleSupplierLocationSerializer(
                data = request.data,
                context = {'supplier': self.supplier}
            )
            location_serializer.is_valid(raise_exception = True)
            location = location_serializer.save()

            data = self.get_serializer(location).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( operation_id = "Retrieve operative location", tags = ["Supplier Locations"],
        responses = { 404: openapi.Response("Not Found")}, security = [{ "api-key": [] }])
    def retrieve(self, request, *args, **kwargs):
        """Endpoint to retrieve a location where a supplier operates by its id"""

        response = super(SupplierLocationViewSet, self).retrieve(request, *args, **kwargs)

        data = response.data
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
