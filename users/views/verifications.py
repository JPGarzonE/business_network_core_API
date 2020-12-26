"""Verification views."""

# Django
from django.utils.decorators import method_decorator
from django.db import transaction
 
# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from users.permissions import IsAccountOwner

# Models
from users.models import User, Verification
from companies.models import Company
from multimedia.models import Document

# Permissions
from users.permissions import IsAccountOwnerOrIsAdmin
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)

# Serializer
from multimedia.serializers import DocumentModelSerializer
from users.serializers import VerificationModelSerializer, HandleVerificationSerializer, generate_verification_token


class UserVerificationAPIView(APIView):
    """
    User verification view set
    
    Handle update and retrive of the verification of a user
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema( tags = ["User Verifications", "Me"], security = [{ "api-key": []}],
        responses = { 200: VerificationModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} })}
    )
    def get(self, request, format = None):
        """Retrieve User Verification\n
            Endpoint to retrieve the verification of the requester user.
        """

        verification = self.get_object(request)

        data = VerificationModelSerializer( verification ).data
        return Response(data, status.HTTP_200_OK)


    @swagger_auto_schema( tags = ["User Verifications"], security = [{ "api-key": [] }],
        request_body = HandleVerificationSerializer,
        responses = { 200: VerificationModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request") }
    )
    @transaction.atomic
    def patch(self, request, user_id = None):
        """Upload Verification Certificates\n
            Endpoint to upload the verification certificates that are required for verify a company.
        """
        
        instance = self.get_object(request)

        vertification_serializer = HandleVerificationSerializer(
            instance = instance,
            data = request.data,
            context = {'user': request.user},
            partial = True
        )

        vertification_serializer.is_valid(raise_exception = True)
        verification = vertification_serializer.save()

        data = VerificationModelSerializer( verification ).data
        data_status = status.HTTP_200_OK

        return Response( data, data_status )


    def get_object(self, request):
        return request.user.verification


class UserVerificationTokenAPIView(APIView):
    """User verification token API view
    
    Retrieve the verification token of a user
    """

    permission_classes = [IsAccountOwnerOrIsAdmin]

    @swagger_auto_schema( tags = ["User Verifications"], security = [{"api-key": ["User owner or admin required"]}],
        responses = { 200: openapi.Response("OK", examples = {"application/json": 
                {'token': 'token'}} ), 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }) 
        })
    def get(self, request, format = None, **kwargs):
        """User Verification Token\n
            Endpoint to retrieve the verification token of a user.
            This token is unique for each user and is used for verify the account of that user.\n
            For retrieve this token is required to be the user owner of the token or have admin level permissions.
        """

        user = self.get_account_entity()
        verification_token = generate_verification_token(user)

        data = {
            "token": verification_token
        }

        return Response(data, status.HTTP_200_OK)

    def get_account_entity(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username = username)

        return user