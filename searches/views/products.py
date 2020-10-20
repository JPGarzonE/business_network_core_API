# searches/views/products.py

# Django
from django.db.models import Q

# django rest framework
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets, filters, generics
from rest_framework.response import Response

# Abastract Syntax Tree
import ast
import json

# Models
from market.models import ShowcaseProduct

# Serializers
from market.serializers.showcases import ShowcaseProductModelSerializer

class SearchShowcaseProductsViewSet(viewsets.GenericViewSet,
                                    generics.ListAPIView):
    """
    Search view in charge of searching queries in showcase products
    """

    serializer_class = ShowcaseProductModelSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['name', 'tariff_heading', 'description', 'company_name', 'company_username']

    def get_query_fields(self):
        """Return the list of query_fields"""
        query_fields_str = self.request.query_params.get("query_fields")

        if query_fields_str is not None:
            query_fields_str = query_fields_str.replace(" ", "")
            return query_fields_str.split(",")
        else:
            return None

    def get_query_statement(self, query):
        query_fields = self.get_query_fields()
        query_statement = Q(pk__in=[]) # This Q statement not returns anything
        query_fields_empty = not query_fields
        
        if query_fields_empty or 'name' in query_fields:
            query_statement = Q(name__unaccent__icontains = query)

        if query_fields_empty or 'description' in query_fields:
            query_statement |= Q(description__unaccent__icontains = query)

        if query_fields_empty or 'tariff_heading' in query_fields:
            query_statement |= Q(tariff_heading__unaccent__icontains = query)

        if query_fields_empty or 'company_name' in query_fields:
            query_statement |= Q(company_name__unaccent__icontains = query)

        return query_statement

    def get_queryset(self):
        """Obtain the query_fields and execute the query over them.
            Then return all the matched results.
        """
        query = self.request.query_params.get("q")
        
        if query is None:
            raise Exception("q query param is needed to search")

        return ShowcaseProduct.objects.filter( self.get_query_statement(query) )

    def list(self, request, *args, **kwargs):
        try:
            products_queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(products_queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            res_data = {
                "results": self.get_serializer(products_queryset, many=True).data
            }
            res_status = status.HTTP_200_OK
        except Exception as e:
            res_data = {"detail": str(e)}
            res_status = status.HTTP_400_BAD_REQUEST

        return Response(res_data, res_status)
    