# searches/views/companies.py

# django rest framework
from rest_framework import mixins, status, viewsets, filters, generics
from django_filters.rest_framework import DjangoFilterBackend

# other local apps
    # Models
from companies.models import Company
    # Serializers
from companies.serializers import CompanyModelSerializer

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
    