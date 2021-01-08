# Views products

# Constants
from companies.constants import VisibilityState

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# Django
from django.db import transaction
from django.utils.decorators import method_decorator
from django.http import Http404

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import SupplierProfile, Product, ProductCertificate, ProductImage
from multimedia.models import Image

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission

# Serializers
from ..serializers import ProductDetailModelSerializer, ProductOverviewModelSerializer, HandleSupplierProductSerializer

# Signals
from .. import signals


@method_decorator( name = 'destroy', decorator = swagger_auto_schema( operation_id = "Delete a product", tags = ["Products"],
        operation_description = "Endpoint to delete a supplier product by its id",
        responses = { 204: "No Content", 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
        }, security = [{ "api-key": [] }]
))
@method_decorator( name = 'update', decorator = swagger_auto_schema(auto_schema = None))
class ProductViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Product view set"""

    serializer_class = ProductDetailModelSerializer
    supplier = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        accountname = kwargs['accountname']
        self.supplier = get_object_or_404(SupplierProfile, company__accountname = accountname)

        return super(ProductViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.supplier

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsSupplierMemberWithEditPermission]
        
        return [permission() for permission in permissions]

    
    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the supplier)"""
        return self.supplier.company


    def get_queryset(self):
        """Return supplier products"""
        return Product.objects.filter(
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the product by the id"""
        product = get_object_or_404(
            Product,
            id = self.kwargs['pk'],
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

        return product

    @swagger_auto_schema( operation_id = "List supplier products", tags = ["Products"],
        operation_description = "Endpoint to list all the products offered by a supplier",
        responses = { 404: openapi.Response("Not Found") }, security = []
    )
    def list(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductOverviewModelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductOverviewModelSerializer(queryset, many=True)

        return Response(serializer.data, status = status.HTTP_200_OK)

    @transaction.atomic
    def perform_destroy(self, instance):
        """Disable product."""
        product_certificates = ProductCertificate.objects.filter( product = instance )
        product_images = ProductImage.objects.filter( product = instance )

        for certificate in product_certificates:
            certificate.delete()
            
        for image in product_images:
            image.delete()

        instance.delete()
        signals.post_product_delete.send(sender=Product, instance = instance)

    @swagger_auto_schema( tags = ["Products"], request_body = HandleSupplierProductSerializer,
        responses = { 200: ProductDetailModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"minimum_purchase": ["This field may not be null"]} 
            })
        }, security = [{ "api-key": [] }])
    def create(self, request, *args, **kwargs):
        """Create a product\n
            Endpoint to create a product owned by a supplier.\n 
            To append complementary data (like certificates or image) to a product you have 
            to append a list with the ids ([189, 243, 2]) of the objects previosuly uploaded,
            this lists are appended in the fields 'certificates' and 'images' respectively. (Request Body below)
        """
        try:
            product_serializer = HandleSupplierProductSerializer(
                data = request.data,
                context = {'supplier': self.supplier}
            )
            product_serializer.is_valid(raise_exception = True)
            product = product_serializer.save()

            data = self.get_serializer(product).data
            data_status = status.HTTP_201_CREATED
        except ValidationError as e:
            raise e
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Products"], request_body = HandleSupplierProductSerializer,
        responses = { 200: ProductDetailModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["This field may not be null"]}
            })
        }, security = [{ "api-key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Partial update a product\n
            Endpoint to update partially a product owned by a supplier.\n 
            When some object id is added in certificates or media, those objects are
            going to be added to the existing ones, not overwritten. To delete a certificate or 
            a media do it through the ProductCertificate or ProductImage delete endpoints
        """
        try:
            instance = self.get_object()
            product_serializer = HandleSupplierProductSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            product_serializer.is_valid(raise_exception = True)
            product = product_serializer.save()

            data = self.get_serializer(product).data
            data_status = status.HTTP_200_OK
        except ValidationError as e:
            raise e
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)


class ProductDetailView(APIView):
    """
        Retrieve the detail of a product.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema( operation_id = "Retrieve a product", tags = ["Products"],
        responses = { 200: ProductDetailModelSerializer, 404: openapi.Response("Not Found")}, security = [])
    def get(self, request, pk, format = None):
        """Endpoint to retrieve the product by the id"""

        try:
            product = self.get_object(pk)
            serializer = ProductDetailModelSerializer(product)

            data = serializer.data
            data_status = status.HTTP_200_OK
        except Http404:
            data = {"detail": "Product not found with the id provided"}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)

    def get_object(self, pk):
        product = get_object_or_404(
            Product,
            id = pk,
            visibility = VisibilityState.OPEN.value
        )

        return product


class DeleteProductImageView(APIView):
    """Product image view to delete."""

    permission_classes = [IsAuthenticated, IsSupplierMemberWithEditPermission]

    product = None
    image = None
    product_image = None
    is_principal_image = None

    @swagger_auto_schema( tags = ["Products"],
        responses = { 204: openapi.Response("No Content", examples = {"application/json": 
            {"detail": "Succesfully deleted"} }),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": 
                "You don't have permission. You're not the owner of the data."} }),
            404: openapi.Response("Not Found", examples = {"application/json":
               {"detail": "Product image not found with the id provided"}
            })
        }, security = [{ "api-key": [] }])
    def delete(self, request, product_id, image_id, format=None):
        """Delete a product image \n
        Endpoint to delete an image from a product. (You have to be the owner of the product)\n
        If you want to delete definitely the image in your galery do it through the Image delete endpoint."""

        try:
            self.product = Product.objects.get( id = product_id ) if not self.product else self.product
            self.image = Image.objects.get( id = image_id ) if not self.image else self.image
            
            product_image = self.get_object()
            
            if self.is_principal_image is True:
                self.product.principal_image = None
                self.product.save()
            else:
                product_image.delete()

            data = {"detail": "Succesfully deleted"}
            data_status = status.HTTP_204_NO_CONTENT
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)

    def get_object(self):
        product_id = self.kwargs.get('product_id')
        image_id = self.kwargs.get('image_id')

        try:
            self.product = Product.objects.get( id = product_id )
        except Product.DoesNotExist:
            raise Exception("Product not found with the id = {}".format(product_id))

        try:
            self.image = Image.objects.get( id = image_id )
        except Image.DoesNotExist:
            raise Exception("Image not found with the id = {}".format(image_id))

        if self.product.principal_image == self.image:
            self.is_principal_image = True
            return self.product.principal_image

        try:
            product_image = ProductImage.objects.get(
                product = self.product,
                image = self.image
            )
        except ProductImage.DoesNotExist:
            raise Exception("The product with the id {} has no image with id {}".format(product_id, image_id))

        return product_image

    def get_data_owner_company(self):
        """Return the company owner of the data 
        (The company of the supplier that is the product owner)
        """

        product_image = self.get_object()
        product = self.product if  self.is_principal_image is True else product_image.product

        return product.supplier.company



class DeleteProductCertificateView(APIView):
    """Product certificate view to delete."""

    permission_classes = [IsAuthenticated, IsSupplierMemberWithEditPermission]

    @swagger_auto_schema( tags = ["Products"],
        responses = { 204: openapi.Response("No Content", examples = {"application/json": 
            {"detail": "Succesfully deleted"} }), 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": 
                "You don't have permission. You're not the owner of the data."} })
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

    def get_data_owner_company(self):
        """Return the company owner of the data 
        (The company of the supplier that is the product owner)
        """

        product_certificate = self.get_object()
        product = product_certificate.product

        return product.supplier.company