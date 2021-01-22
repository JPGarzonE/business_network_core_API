# Views profiles

# Django
from django.http import Http404
from django.db import transaction

# Django rest framework
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import BuyerProfile

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..permissions import IsBuyerMemberWithEditPermission

# Serializers
from ..serializers import BuyerProfileSerializer


class BuyerProfileView(APIView):
    """View for request and update the profile of a buyer."""

    permission_classes = [IsAuthenticated, IsBuyerMemberWithEditPermission]
    buyer = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        accountname = kwargs['accountname']
        self.buyer = get_object_or_404(
            BuyerProfile, 
            company__accountname = accountname
        )

        return super(BuyerProfileView, self).dispatch(request, *args, **kwargs)


    @swagger_auto_schema( operation_id = "Retrieve Buyer Profile", tags = ["Profiles"],
        responses = { 200: BuyerProfileSerializer, 404: openapi.Response("Not Found")}, security = []
    )
    def get(self, request, accountname, format = None):
        """Return the profile of a buyer with the accountname given by param."""

        try:
            profile_serializer = BuyerProfileSerializer( self.buyer )
            data = profile_serializer.data
            data_status = status.HTTP_200_OK
        except Http404:
            data = {"detail": "Buyer not found with the accountname provided"}
            data_status = status.HTTP_404_NOT_FOUND

        return Response(data, status = data_status)

    @swagger_auto_schema( tags = ["Profiles"], security = [{ "api-key": [] }],
        request_body = BuyerProfileSerializer,
        responses = { 200: BuyerProfileSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request") }
    )
    @transaction.atomic
    def patch(self, request, accountname):
        """Update Buyer Profile\n
            Endpoint to update completely the buyer profile.
        """

        profile_serializer = BuyerProfileSerializer(
            instance = self.buyer,
            data = request.data,
            partial = True
        )

        profile_serializer.is_valid(raise_exception = True)
        buyer_profile = profile_serializer.save()

        data = BuyerProfileSerializer( buyer_profile ).data
        
        return Response( data, status.HTTP_200_OK )

    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the buyer)"""
        return self.buyer.company
