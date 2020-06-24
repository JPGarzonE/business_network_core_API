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
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Serializer
from multimedia.serializers import DocumentModelSerializer
from users.serializers import VerificationModelSerializer

class UserVerificationAPIView(APIView):
    """
    User verification view set
    
    Handle update and retrive of the verification of a user
    """

    permisssion_classes = [IsAuthenticated]

    def get(self, request, format = None):
        verification = self.get_object(request)

        data = VerificationModelSerializer( verification ).data
        return Response(data, status.HTTP_200_OK)

    @transaction.atomic
    def patch(self, request, user_id = None):
        verification = self.get_object(request)

        if request.data.get("documents"):
            documents = request.data.pop("documents")

            for document in documents:
                document_object = Document.objects.get( id = document.get("id") )
                document_object.verification = verification
                document_object.save()

            verification.state = "InProgress"
            verification.save()

            serializer = VerificationModelSerializer( verification )
            return Response( serializer.data, status = status.HTTP_200_OK )
        else:
            serializer = VerificationModelSerializer( verification, data = request.data, partial = True )

            if serializer.is_valid( raise_exception = True ):
                serializer.save()
                return Response( serializer.data, status = status.HTTP_200_OK )


    def get_object(self, request):
        return request.user.verification