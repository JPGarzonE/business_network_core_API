# Views currencies

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.db import transaction
from django.utils.decorators import method_decorator
from django.http import Http404

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import Currency
 
# Permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
 
# Serializers
from ..serializers import CurrencyModelSerializer


@method_decorator(name='list', decorator = swagger_auto_schema( operation_id = "List currencies", tags = ["Currencies"],
    operation_description = "Endpoint to list all the currencies available in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class CurrencyViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """Currency view set."""

    serializer_class = CurrencyModelSerializer
    
    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAdminUser]
        
        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return all the active currencies"""
        return Currency.objects.filter(is_active = True)

    def get_object(self):
        """Return the currency by the id"""
        currency = get_object_or_404(
            Currency,
            id = self.kwargs['pk'],
            is_active = True
        )

        return currency

    @swagger_auto_schema( tags = ["Currencies"], responses = { 404: openapi.Response("Not Found") }, 
        security = [{ "api-key": ["Is Admin needed"] }]
    )
    def create(self, request, *args, **kwargs):
        """Create a currency\n
            Endpoint to create a currency in the platform
        """
        try:
            currency_serializer = CurrencyModelSerializer(
                data = request.data
            )
            currency_serializer.is_valid(raise_exception = True)
            currency = currency_serializer.save()

            data = self.get_serializer(currency).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Currencies"], responses = { 404: openapi.Response("Not Found") }, 
        security = [{ "api-key": ["Is Admin needed"] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a currency\n
            Endpoint to partial update a currency in the platform
        """

        try:
            instance = self.get_object()
            currency_serializer = CurrencyModelSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            currency_serializer.is_valid(raise_exception = True)
            currency = currency_serializer.save()

            data = self.get_serializer(currency).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)