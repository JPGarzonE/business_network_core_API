"""Company locations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.db import transaction
from django.utils.decorators import method_decorator

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company, Product, ProductCertificate, ProductMedia, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import ProductModelSerializer, HandleCompanyProductSerializer

@method_decorator(name='list', decorator = swagger_auto_schema( operation_id = "List products", tags = ["Products"],
    operation_description = "Endpoint to list all the products of a company",
    responses = { 404: openapi.Response("Not Found") }, security = [{ "Anonymous": [] }]
))
@method_decorator( name = 'destroy', decorator = swagger_auto_schema( operation_id = "Delete a product", tags = ["Products"],
        operation_description = "Endpoint to delete a certificate by its id",
        responses = { 204: {}, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
        }, security = [{ "api_key": [] }]
))
class ProductViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Product view set"""

    serializer_class = ProductModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(ProductViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]
        
        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company products"""
        return Product.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN
        )

    def get_object(self):
        """Return the product by the id"""
        product = get_object_or_404(
            Product,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN
        )

        return product

    @transaction.atomic
    def perform_destroy(self, instance):
        """Disable product."""
        instance.visibility = VisibilityState.DELETED.value

        product_certificates = ProductCertificate.objects.filter( product = instance )
        product_media = ProductMedia.objects.filter( product = instance )

        for certificate in product_certificates:
            certificate.delete()
            
        for media in product_media:
            media.delete()

        instance.save()

    @swagger_auto_schema( tags = ["Products"], request_body = HandleCompanyProductSerializer,
        responses = { 200: ProductModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"minimum_purchase": ["This field may not be null"]} 
            })
        }, security = [{ "api_key": [] }])
    def create(self, request, *args, **kwargs):
        """Create product\n
            Endpoint to create a product.\n 
            To append complementary data (like certificates or media) to a product you have 
            to append a list with the ids ([189, 243, 2]) of the objects previosuly uploaded,
            this lists are appended in the fields 'certificates' and 'media' respectively. (Request Body below)
        """

        product_serializer = HandleCompanyProductSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        product_serializer.is_valid(raise_exception = True)
        product = product_serializer.save()

        data = self.get_serializer(product).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Products"], request_body = HandleCompanyProductSerializer,
        responses = { 200: ProductModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["This field may not be null"]} 
            })
        }, security = [{ "api_key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Partial update a product\n
            Endpoint to update partially a product.\n 
            When some object id is added in certificates or media, those objects are
            going to be added to the existing ones, not overwritten. To delete a certificate or 
            a media do it through the ProductCertificate or ProductMedia delete endpoints
        """
        instance = self.get_object()
        product_serializer = HandleCompanyProductSerializer(
            instance = instance,
            data = request.data,
            partial = True
        )

        product_serializer.is_valid(raise_exception = True)
        product = product_serializer.save()

        data = self.get_serializer(product).data
        data_status = status.HTTP_200_OK
        
        return Response(data, status = data_status)


class ProductDetailView(APIView):
    """
        Retrieve the detail of a product.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema( operation_id = "Retrieve a product", tags = ["Products"],
        responses = { 200: ProductModelSerializer, 404: openapi.Response("Not Found")}, security = [{ "Anonymous": [] }])
    def get(self, request, pk, format = None):
        """Endpoint to retrieve the product by the id"""
        product = self.get_object(pk)
        serializer = ProductModelSerializer(product)

        return Response(serializer.data)

    def get_object(self, pk):
        product = get_object_or_404(
            Product,
            id = pk,
            visibility = VisibilityState.OPEN
        )

        return product