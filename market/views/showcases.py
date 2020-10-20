"""Market showcases views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

# Django
from django.db import transaction
from django.utils.decorators import method_decorator
from django.http import Http404

# Serializers
from market.serializers.showcases import ShowcaseSerializer, ShowcaseSectionModelSerializer

# Model
from market.models import ShowcaseProduct, ShowcaseSection


class ShowcaseFeedView(ListAPIView):
    """Lists all the data feed belonging to the market
    
        The data contains products divided by categories.
    """

    queryset = ShowcaseSection.objects.all()
    serializer_class = ShowcaseSectionModelSerializer

    def list(self, request, *args, **kwargs):
        showcase_section_queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(showcase_section_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(showcase_section_queryset, many=True)

        data = serializer.data
        response_status = status.HTTP_200_OK

        return Response(data, response_status)