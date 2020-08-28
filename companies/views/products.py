"""Company locations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company, Product, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import ProductModelSerializer, HandleCompanyProductSerializer

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

    def perform_destroy(self, instance):
        """Disable product."""
        instance.visibility = VisibilityState.DELETED
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Product creation."""
        product_serializer = HandleCompanyProductSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        product_serializer.is_valid(raise_exception = True)
        product = product_serializer.save()

        data = self.get_serializer(product).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def partial_update(self, request, *args, **kwargs):
        """Handle product partial update and add a 
        media to a product by its id if its the case"""
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

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format = None):
        """Return the product by the id"""
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