"""Company certificates views."""

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
from companies.models import Company, Certificate, CompanyCertificate, ProductCertificate, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner, IsPredominantEntiyOwner

# Serializers
from companies.serializers import (
    CertificateModelSerializer, 
    CompanyCertificateModelSerializer, 
    CreateCompanyCertificateSerializer,
    UpdateCertificateSerializer
)


@method_decorator(name='list', decorator = swagger_auto_schema( 
    operation_id = "List company certificates", tags = ["Supplier Certificates"],
    operation_description = "Endpoint to list all the certificates of a company user",
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
    operation_id = "Retrieve a company certificate", tags = ["Supplier Certificates"], security = [],
    operation_description = "Endpoint to retrieve a certificate owned by a company according its id.",
    responses = { 200: CompanyCertificateModelSerializer, 404: openapi.Response("Not Found")}
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class CompanyCertificateViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    """Company certificate view set."""

    serializer_class = CompanyCertificateModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(CompanyCertificateViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return tge entity father of the data"""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return company certificates"""
        company_certificate = CompanyCertificate.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN.value
        )

        return company_certificate
    
    def get_object(self):
        """Return the company certificate by the id"""
        company_certificate = get_object_or_404(
            CompanyCertificate,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return company_certificate

    def perform_destroy(self, instance):
        """Disable certificate."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    @swagger_auto_schema( tags = ["Supplier Certificates"], request_body = CreateCompanyCertificateSerializer,
        responses = { 200: CompanyCertificateModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "The body data must have at least a name for the certificate creation or a certificate_id for associating to a existing certificate."} 
            })
        }, security = [{ "api-key": [] }]
    )
    def create(self, request, *args, **kwargs):
        """Create company certificate\n
            Endpoint to create a company certificate.\n 
            The request body recieves either a certificate_id value for associating 
            to an existing certificate, or, it recieves the certificate data (name, description, image_id)
            where at least the name is needed.
        """
        try:
            certificate_serializer = CreateCompanyCertificateSerializer(
                data = request.data,
                context = {'company': self.company}
            )
            certificate_serializer.is_valid(raise_exception = True)
            company_certificate = certificate_serializer.save()

            data = self.get_serializer(company_certificate).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status = data_status)

    @swagger_auto_schema( operation_id = "Partial update company certificate", tags = ["Supplier Certificates"], request_body = UpdateCertificateSerializer,
        responses = { 200: CompanyCertificateModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["This field may not be null"]} 
            })
        }, security = [{ "api-key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Enpoint to update partially a company certificate"""
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
        The difference between this one and the company certificate is that company certificate is explicitly 
        owned by a company, while the existence of a normal certificate is indepent from other entities."""

        certificate = self.get_object(pk)
        serializer = CertificateModelSerializer(certificate)

        return Response(serializer.data)


    def get_object(self, pk):
        certificate = get_object_or_404(
            Certificate,
            id = pk
        )

        return certificate


class DeleteProductCertificateView(APIView):
    """Product certificate view to delete."""

    permission_classes = [IsAuthenticated, IsPredominantEntiyOwner]

    @swagger_auto_schema( tags = ["Products"],
        responses = { 204: openapi.Response("No Content", examples = {"application/json": 
            {"detail": "Succesfully deleted"} }), 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": 
                "You don't have permission. You're not the owner of the data."} }),
            404: openapi.Response("Not Found", examples = {"application/json":
               {"detail": "Product image not found with the id provided"}
            })
        }, security = [{ "api-key": [] }])
    def delete(self, request, product_id, certificate_id, format=None):
        """Delete a product certificate \n
        Endpoint to delete a certificate from a product. (You have to be the owner of the product)\n"""

        try:
            product_certificate = self.product_certificate if self.product_certificate else self.get_object()
            product_certificate.delete()

            data = {"detail": "Succesfully deleted"}
            data_status = status.HTTP_204_NO_CONTENT
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)


    def get_object(self):
        product_id = self.kwargs.get('product_id')
        certificate_id = self.kwargs.get('certificate_id')

        try:
            self.product_certificate = ProductCertificate.objects.get(
                product__id = product_id,
                certificate__id = certificate_id
            )
        except ProductCertificate.DoesNotExist:
            raise Exception("Product certificate not found with the both ids provided")

        return self.product_certificate


    def get_predominant_entity_owner(self):
        product_certificate = self.get_object()
        product = product_certificate.product
        company = product.company

        return company