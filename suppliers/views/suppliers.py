# Views suppliers

# Django
from django.utils.decorators import method_decorator

# Django-rest framework
from rest_framework import mixins, status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company
from ..models import SupplierProfile
 
# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission
 
# Serializers
from ..serializers import (
    ActivateSupplierSerializer,
    SupplierProfileModelSerializer, 
    UpdateSupplierSerializer, 
    SupplierSummarySerializer, 
    UpdateSupplierSummarySerializer
)


@method_decorator(name = 'list', decorator = swagger_auto_schema( operation_id = "List suppliers", tags = ["Suppliers"],
    operation_description = "Endpoint to list all the supplier registered in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve a supplier", tags = ["Suppliers"],
    operation_description = """Endpoint to retrieve the supplier of a company registered in 
        the platform by the company accountname""",
    responses = { 200: SupplierProfileModelSerializer, 404: openapi.Response("Not Found")}, security = []
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class SupplierViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin, 
                    viewsets.GenericViewSet):
    """Supplier view set."""

    serializer_class = SupplierProfileModelSerializer
    lookup_field = 'accountname'
    lookup_value_regex = "[\\w.]+"

    def get_queryset(self):
        """Return suppliers."""

        return SupplierProfile.objects.all()

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve', 'list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsSupplierMemberWithEditPermission]

        return [permission() for permission in permissions]


    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the supplier)"""
        print(self.action)

        if self.action in ['activate']:
            self.company = get_object_or_404(
                Company, accountname = self.kwargs['accountname']
            )
            return self.company
        else:
            return self.get_object().company
 

    def get_object(self):
        return get_object_or_404(
            SupplierProfile,
            company__accountname = self.kwargs['accountname']
        )

    @swagger_auto_schema( operation_id = "Partial update a supplier", tags = ["Suppliers"], request_body = UpdateSupplierSerializer,
        responses = { 200: SupplierProfileModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"display_name": ["max 60 characters"]}
            })
        }, security = [{ "api-key": [] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a supplier model."""
        try:
            instance = self.get_object()
            supplier_serializer = UpdateSupplierSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            supplier_serializer.is_valid(raise_exception = True)
            supplier = supplier_serializer.save()

            data = self.get_serializer(supplier).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Companies", "Suppliers"], request_body = serializers.Serializer(),
        manual_parameters = [
            openapi.Parameter(name = "accountname", in_ = openapi.IN_PATH, type = "String",
                description = "accountname of the company that is going to be extended as a supplier.")
        ],
        responses = { 201: ActivateSupplierSerializer }, security = [{ "api-key": [] }]
    )
    @action(detail = True, methods = ['post'])
    def activate(self, request, accountname):
        """Activate as a supplier\n
        Endpoint to activate a company as a supplier.\n
        Recieves the accountname of the company by param and extends the
        company account to perform supplier actions in the platform.
        """
        if self.company is None:
            self.company = get_object_or_404(
                Company, accountname = accountname
            )

        activate_serializer = ActivateSupplierSerializer(
            data = {},
            context = { 'company': self.company } 
        )
        activate_serializer.is_valid(raise_exception = True)

        supplier = activate_serializer.save()
        supplier_serializer = ActivateSupplierSerializer( supplier )

        return Response( supplier_serializer.data, status = status.HTTP_201_CREATED )


@method_decorator(name = 'retrieve', decorator = swagger_auto_schema( operation_id = "Retrieve a supplier summary", tags = ["Suppliers"],
    operation_description = "Endpoint to retrieve the summary of a supplier",
    responses = { 200: SupplierSummarySerializer, 404: openapi.Response("Not Found")}, security = []
))
class SupplierSummaryViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, 
                            viewsets.GenericViewSet):
    """View set of the main summary of a supplier"""

    serializer_class = SupplierSummarySerializer
    supplier = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the supplier exists"""
        self.supplier = self.get_queryset()

        return super(SupplierSummaryViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsSupplierMemberWithEditPermission]
        
        return [permission() for permission in permissions]

    
    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the supplier)"""
        return self.supplier.company
 

    def get_queryset(self):
        accountname = self.kwargs['accountname']
        return get_object_or_404(
            SupplierProfile, company__accountname = accountname
        )

    def get_object(self):
        return self.supplier

    @swagger_auto_schema( operation_id = "Update a supplier summary", tags = ["Suppliers"], request_body = UpdateSupplierSummarySerializer,
        responses = { 200: SupplierSummarySerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["max 60 characters"]}
            })
        }, security = [{ "api-key": [] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Endpoint to partial update the summary of a supplier"""
        try:
            instance = self.get_object()
            supplier_serializer = UpdateSupplierSummarySerializer(
                instance = instance,
                data = request.data,
                context = {"supplier": self.supplier},
                partial = True
            )

            supplier_serializer.is_valid(raise_exception = True)
            supplier = supplier_serializer.save()

            data = self.get_serializer(supplier).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)