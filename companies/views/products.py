"""Company locations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Models
from companies.models import Company, Product, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import ProductModelSerializer, CreateCompanyProductSerializer

class ProductViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Product view set"""

    serializer_class = ProductModelSerializer

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
        elif self.action in ['retrieve']:
            permissions = [IsDataOwner]
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
        product_serializer = CreateCompanyProductSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        product_serializer.is_valid(raise_exception = True)
        product = product_serializer.save()

        data = self.get_serializer(product).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(ProductViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'product': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
