# View sale_locations

# Constant
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
from ..models import SupplierProfile, SupplierSaleLocation

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission

# Serializers
from ..serializers import SupplierSaleLocationModelSerializer, HandleSupplierSaleLocationSerializer

# Utils
from distutils.util import strtobool


@method_decorator(name='list', decorator = swagger_auto_schema( 
    operation_id = "List supplier sale locations", tags = ["Supplier Locations"],
    operation_description = "Endpoint to list all the locations where a supplier sales." ,
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name='destroy', decorator = swagger_auto_schema(
    operation_id = "Delete a sale location", tags = ["Supplier Locations"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete a sale location of a supplier by company accountname and location id.",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve sale location", tags = ["Supplier Locations"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to retrieve a location where a supplier sales by its id.",
    responses = { 200: SupplierSaleLocationModelSerializer, 404: openapi.Response("Not Found")}
))
@method_decorator(name = 'update', decorator = swagger_auto_schema(auto_schema = None))
class SupplierSaleLocationViewSet(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """Supplier Sale Location view set"""

    serializer_class = SupplierSaleLocationModelSerializer
    supplier = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the supplier exists"""
        accountname = kwargs['accountname']
        self.supplier = get_object_or_404(
            SupplierProfile, company__accountname = accountname,
            visibility = VisibilityState.OPEN.value
        )

        return super(SupplierSaleLocationViewSet, self).dispatch(request, *args, **kwargs)

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
        return SupplierSaleLocation.objects.filter(
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the location by the id"""
        location = get_object_or_404(
            SupplierSaleLocation,
            id = self.kwargs['pk'],
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

        return location

    def perform_destroy(self, instance):
        """Disable location."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()


    @swagger_auto_schema( operation_id = "Create sale location", tags = ["Supplier Locations"],
        request_body = HandleSupplierSaleLocationSerializer, security = [{ "api-key": [] }],
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": 
                {"detail": "Authentication credentials were not provided"} 
            }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} 
            })
        })
    def create(self, request, *args, **kwargs):
        """Endpoint to create a location where the supplier sales."""
        try:
            location_serializer = HandleSupplierSaleLocationSerializer(
                data = request.data,
                context = {'suplier': self.supplier}
            )
            location_serializer.is_valid(raise_exception = True)
            location = location_serializer.save()

            data = self.get_serializer(location).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    
    @swagger_auto_schema( operation_id = "Partial update sale location", tags = ["Supplier Locations"],
        responses = { 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"country": ["This field may not be null"]} 
            })
        }, request_body = SupplierSaleLocationModelSerializer, security = [{ "api-key": [] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Endpoint to update partially a location where a supplier sales. 
            It is partial, so its not needed pass all the body values
        """

        try:
            instance = self.get_object()
            serializer = HandleSupplierSaleLocationSerializer(
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