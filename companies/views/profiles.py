"""Profiles views py"""

# Django
from django.http import Http404

# Django rest framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Models
from companies.models import Company, VisibilityState

# Permissions
from rest_framework.permissions import AllowAny

# Serializers
from companies.serializers import SupplierProfileSerializer


class CompanyProfileView(APIView):
    """View for request the profile of a company."""

    permission_classes = [AllowAny]

    def get(self, request, username, format = None):
        """Return the profile of the company by param."""
        try:
            company = self.get_object(username)
            profile_company = {
                'company': company
            }
            profile_serializer = SupplierProfileSerializer(
                profile_company,
                context = {'request': request}
            )
            # profile_serializer.is_valid(raise_exception = True)
            data = profile_serializer.data
            data_status = status.HTTP_200_OK
        except Http404:
            data = {"detail": "Company not found with the username provided"}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)

    def get_object(self, username):
        return get_object_or_404(
            Company,
            user__username = username,
            visibility = VisibilityState.OPEN.value
        )