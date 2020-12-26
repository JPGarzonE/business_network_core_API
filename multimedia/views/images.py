# Videos views

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
from multimedia.models import Image

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Serializer
from multimedia.serializers import ImageModelSerializer, CreateImageSerializer


@method_decorator( name = 'list', decorator = swagger_auto_schema( 
    operation_id = "List images", tags = ["Images"],
    operation_description = "Endpoint to list all the images uploaded in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve an image", tags = ["Images"], security = [],
    operation_description = "Endpoint to retrieve an image previously uploaded by its id.",
    responses = { 200: ImageModelSerializer, 404: openapi.Response("Not Found")}
))
class ImageViewSet(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """Image view set"""

    serializer_class = ImageModelSerializer
    queryset = Image.objects.all()
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
        image = get_object_or_404(
            Image,
            id = self.kwargs['pk']
        )

        return image


    @swagger_auto_schema( tags = ["Images"], request_body = CreateImageSerializer,
        responses = { 200: ImageModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json": {"image": ["This field required"]} })
        }, security = [{ "api-key": [] }]
    )
    def create(self, request, *args, **kwargs):
        """Upload an image\n
            Endpoint to upload an image to the platform. The image will register whose the user that uploaded it.\n
            The request body schema has to be of `multipart/form-data`.
        """

        # The user is identified by its auth token
        user = request.user

        image_serializer = CreateImageSerializer(
            data = request.data,
            context = {'user': user}
        )

        image_serializer.is_valid(raise_exception = True)
        image = image_serializer.save()

        data = self.get_serializer(image).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)