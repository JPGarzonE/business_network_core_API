# File views

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
# Models
from multimedia.models import Document

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Serializer
from multimedia.serializers import DocumentModelSerializer, CreateDocumentSerializer

class FileViewSet(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """File view set"""

    serializer_class = DocumentModelSerializer
    queryset = Document.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        """Assign permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def get_object(self):
        document = get_object_or_404(
            Document,
            id = self.kwargs['pk']
        )

        return document

    def create(self, request, *args, **kwargs):
        """Handle files creation"""
        # The user is identified by its auth token
        user = request.user

        document_serializer = CreateDocumentSerializer(
            data = request.data,
            context = {'user': user}
        )

        document_serializer.is_valid(raise_exception = True)
        document = document_serializer.save()

        data = self.get_serializer(document).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)