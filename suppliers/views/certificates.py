# Views certificates

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.utils.decorators import method_decorator
from django.http import Http404

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import SupplierProfile, Certificate, SupplierCertificate, ProductCertificate

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission

# Serializers
from ..serializers import (
    CertificateModelSerializer, 
    SupplierCertificateModelSerializer, 
    CreateSupplierCertificateSerializer,
    UpdateCertificateSerializer
)


@method_decorator(name='list', decorator = swagger_auto_schema( 
    operation_id = "List supplier certificates", tags = ["Supplier Certificates"],
    operation_description = "Endpoint to list all the certificates of a supplier",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'destroy', decorator = swagger_auto_schema( 
    operation_id = "Delete a certificate", tags = ["Supplier Certificates"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete a certificate by its id",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve a supplier certificate", tags = ["Supplier Certificates"], security = [],
    operation_description = "Endpoint to retrieve a certificate owned by a supplier according its id.",
    responses = { 200: SupplierCertificateModelSerializer, 404: openapi.Response("Not Found")}
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class SupplierCertificateViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """Supplier certificate view set."""

    serializer_class = SupplierCertificateModelSerializer
    supplier = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the supplier exists"""
        accountname = kwargs['accountname']
        self.supplier = get_object_or_404(SupplierProfile, company__accountname = accountname)

        return super(SupplierCertificateViewSet, self).dispatch(request, *args, **kwargs)

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
        """Return supplier certificates"""
        supplier_certificates = SupplierCertificate.objects.filter(
            supplier = self.supplier
        )

        return supplier_certificates
    
    def get_object(self):
        """Return the supplier certificate by the id"""
        supplier_certificate = get_object_or_404(
            SupplierCertificate,
            id = self.kwargs['pk'],
            supplier = self.supplier
        )

        return supplier_certificate

    @swagger_auto_schema( tags = ["Supplier Certificates"], request_body = CreateSupplierCertificateSerializer,
        responses = { 200: SupplierCertificateModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "The body data must have at least a name for the certificate creation or a certificate_id for associating to a existing certificate."} 
            })
        }, security = [{ "api-key": [] }]
    )
    def create(self, request, *args, **kwargs):
        """Create supplier certificate\n
            Endpoint to create a supplier certificate.\n 
            The request body recieves either a certificate_id value for associating 
            to an existing certificate, or, it recieves the certificate data (name, description, image_id)
            where at least the name is needed.
        """
        try:
            certificate_serializer = CreateSupplierCertificateSerializer(
                data = request.data,
                context = {'supplier': self.supplier}
            )
            certificate_serializer.is_valid(raise_exception = True)
            supplier_certificate = certificate_serializer.save()

            data = self.get_serializer(supplier_certificate).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status = data_status)

    @swagger_auto_schema( operation_id = "Partial update supplier certificate", tags = ["Supplier Certificates"], 
        request_body = UpdateCertificateSerializer, security = [{ "api-key": [] }],
        responses = { 200: SupplierCertificateModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["This field may not be null"]} 
            })
        })
    def partial_update(self, request, *args, **kwargs):
        """Enpoint to update partially a supplier certificate"""
        try:
            instance = self.get_object()
            certificate_serializer = UpdateCertificateSerializer(
                instance = instance.certificate,
                data = request.data,
                partial = True
            )

            certificate_serializer.is_valid(raise_exception = True)
            certificate = certificate_serializer.save()
            instance.certificate = certificate

            data = self.get_serializer(instance).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status = data_status)


class CertificateDetailView(APIView):
    """Endpoint to retrieve a certificate with its details by the id."""

    permission_classes = [AllowAny]

    @swagger_auto_schema( tags = ["Supplier Certificates"],
        responses = { 200: CertificateModelSerializer, 404: openapi.Response("Not Found")}, security = [])
    def get(self, request, pk, format = None):
        """Retrieve certificate detail\n
        Endpoint to retrieve certificate by its id.\n
        The difference between this one and the supplier certificate is that supplier certificate is explicitly 
        owned by a supplier, while the existence of a normal certificate is indepent from other entities."""

        certificate = self.get_object(pk)
        serializer = CertificateModelSerializer(certificate)

        return Response(serializer.data)


    def get_object(self, pk):
        certificate = get_object_or_404(
            Certificate,
            id = pk
        )

        return certificate