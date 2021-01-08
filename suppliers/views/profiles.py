# Views profiles

# Constants
from companies.constants import VisibilityState

# Django
from django.http import Http404

# Django rest framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import SupplierProfile

# Permissions
from rest_framework.permissions import AllowAny

# Serializers
from ..serializers import SupplierProfileSerializer, DocumentationSupplierProfileSerializer


class SupplierProfileView(APIView):
    """View for request the profile of a supplier."""

    permission_classes = [AllowAny]

    @swagger_auto_schema( operation_id = "Retrieve Supplier Profile", tags = ["Profiles"],
        responses = { 200: DocumentationSupplierProfileSerializer, 404: openapi.Response("Not Found")}, security = []
    )
    def get(self, request, accountname, format = None):
        """Return the profile of a supplier with the accountname given by param."""

        try:
            supplier = self.get_object(accountname)
            profile_supplier = {
                'supplier': supplier
            }
            profile_serializer = SupplierProfileSerializer(
                profile_supplier,
                context = {'request': request}
            )

            data = profile_serializer.data
            data_status = status.HTTP_200_OK
        except Http404:
            data = {"detail": "Supplier not found with the accountname provided"}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)

    def get_object(self, accountname):
        return get_object_or_404(
            SupplierProfile,
            company__accountname = accountname,
            visibility = VisibilityState.OPEN.value
        )