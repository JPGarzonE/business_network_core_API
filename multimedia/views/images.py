# Videos views

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Django
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
# Models
from multimedia.models import Media

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

# Serializer
from multimedia.serializers import MediaModelSerializer, CreateImageSerializer

class ImageViewSet(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """Image view set"""

    serializer_class = MediaModelSerializer
    queryset = Media.objects.all()
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
        media = get_object_or_404(
            Media,
            id = self.kwargs['pk']
        )

        return media

    def create(self, request, *args, **kwargs):
        """Handle images creation"""
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