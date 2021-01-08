# Views files

# Django
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from multimedia.models import File

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Serializer
from multimedia.serializers import FileModelSerializer, CreateFileSerializer


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List files", tags = ["Files"],
    operation_description = "Endpoint to list all the files uploaded in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve a file", tags = ["Files"], security = [],
    operation_description = "Endpoint to retrieve a file previously uploaded by its id.",
    responses = { 200: FileModelSerializer, 404: openapi.Response("Not Found")}
))
class FileViewSet(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """File view set"""

    serializer_class = FileModelSerializer
    queryset = File.objects.all()
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
        file = get_object_or_404(
            File,
            id = self.kwargs['pk']
        )

        return file

    @swagger_auto_schema( tags = ["Files"], request_body = CreateFileSerializer,
        responses = { 200: FileModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json": {"file": ["This field required"]} })
        }, security = [{ "api-key": [] }]
    )
    def create(self, request, *args, **kwargs):
        """Upload a file\n
            Endpoint to upload a file to the platform. The file will register whose the user that uploaded it.\n
            The request body schema has to be of `multipart/form-data`.
        """

        # The user is identified by its auth token
        user = request.user

        file_serializer = CreateFileSerializer(
            data = request.data,
            context = {'user': user}
        )

        file_serializer.is_valid(raise_exception = True)
        file = file_serializer.save()

        data = self.get_serializer(file).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)