# searches/views/companies.py

# Django
from django.utils.decorators import method_decorator

# django rest framework
from rest_framework import mixins, status, viewsets, filters, generics
from django_filters.rest_framework import DjangoFilterBackend

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# other local apps
    # Models
from companies.models import Company, UnregisteredCompany
    # Serializers
from companies.serializers import CompanyModelSerializer, UnregisteredCompanyModelSerializer


@method_decorator(name = 'list', decorator = swagger_auto_schema(
    operation_id = "Search Companies", tags = ["Search"],
    operation_description = "Endpoint to search a company in the platform by a query given.",
    manual_parameters = [
        openapi.Parameter(name = "industry", in_ = openapi.IN_QUERY, type = "String",
            description = "Param for filter the companies search by industry.")
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
class SearchCompaniesViewSet(viewsets.GenericViewSet,
                            generics.ListAPIView):
    """
    Search view in charge of searching queries in companies model.
    """

    queryset = Company.objects.all()
    serializer_class = CompanyModelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'description']
    filterset_fields = ['industry']


@method_decorator(name = 'list', decorator = swagger_auto_schema(
    operation_id = "Search Unregistered Companies", tags = ["Search"],
    operation_description = "Endpoint to search an unregistered company in the platform by a query given.",
    manual_parameters = [
        openapi.Parameter(name = "industry", in_ = openapi.IN_QUERY, type = "String",
            description = "Param for filter the unregistered companies search by industry.")
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
class SearchUnregisteredCompaniesViewSet(viewsets.GenericViewSet,
                                        generics.ListAPIView):
    """
    Search view in charge of searching queries in unregistered companies model.
    """

    queryset = UnregisteredCompany.objects.all()
    serializer_class = UnregisteredCompanyModelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'email']
    filterset_fields = ['industry']