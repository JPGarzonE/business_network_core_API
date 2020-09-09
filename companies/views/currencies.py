"""Currency views."""

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

# Serializers
from companies.serializers import CurrencyModelSerializer

# Permissions
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

# Models
from companies.models import Currency

@method_decorator(name='list', decorator = swagger_auto_schema( operation_id = "List currencies", tags = ["Currencies"],
    operation_description = "Endpoint to list all the currencies available in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = [{ "Anonymous": [] }]
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class CurrencyViewSet(mixins.ListModelMixin,
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

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs):
        """Create a currency"""
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

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        """Partial update a currency"""
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