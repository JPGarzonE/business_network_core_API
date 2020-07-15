"""Verification views."""

# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from django.db import transaction

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

    def get(self, request, format = None):
        verification = self.get_object(request)

        data = VerificationModelSerializer( verification ).data
        return Response(data, status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, user_id = None):
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
    """
    User verification view set
    
    Handle update and retrive of the verification of a user
    """

    permission_classes = [IsAccountOwnerOrIsAdmin]

    def get(self, request, format = None, **kwargs):
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