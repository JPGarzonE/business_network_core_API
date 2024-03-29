# Serializer images

# OS
import os

# Django rest framework
from rest_framework import serializers

# Django
from django.core.files.images import get_image_dimensions
from django.db import transaction

# Models
from multimedia.models import Image

# Storages
from multimedia.storages import ImageStorage


def serialize_image_relative_path(image_relative_path):
    """Method that take the relative path of an uploaded
    image in s3 and returns the signed path for that image."""

    image_storage = ImageStorage()

    return image_storage.url(image_relative_path)


class ImageModelSerializer(serializers.ModelSerializer):
    """Image model serializer."""

    path = serializers.SerializerMethodField()

    class Meta:
        """Image meta class."""

        model = Image

        fields = (
            'id',
            'name',
            'path',
            'width',
            'height',
            'type',
            'size',
            'created_date',
            'uploaded'
        )

        read_only_fields = (
            'id',
            'path',
            'width',
            'height',
            'type',
            'size',
            'created_date',
            'uploaded'
        )

    def get_path(self, instance):
        image_path = instance.relative_path

        return serialize_image_relative_path(image_path)


class CreateImageSerializer(serializers.Serializer):
    """
    Serializer in charge of creating the images in the bucket 
    and in the database
    """

    requires_context = True
    
    image = serializers.ImageField(required = True, allow_empty_file = False)

    @transaction.atomic
    def create(self, data):
        """Create and store a new image"""

        # Define an appropiate folder name
        request = self.context.get('request')
        company_accountname = request.auth.payload.get('company_accountname')
        username = request.user.username
        folder_name = company_accountname if company_accountname else username

        image_object = data.get("image")
        
        image_size = image_object.size # size in bytes
        image_width = get_image_dimensions(image_object)[0]
        image_height = get_image_dimensions(image_object)[1]

        _, image_extension = os.path.splitext(image_object.name)

        image = Image.objects.create(
            width = image_width,
            height = image_height,
            size = image_size,
            type = image_extension
        )
        image_id = image.id

        bucket_directory = '{folder_name}/{image_object_id}/'.format( 
            folder_name = folder_name,
            image_object_id = image_id
        )
        
        imagename = '{image_object_id}{image_extension}'.format(
            image_object_id = image_id,
            image_extension = image_extension
        )
        
        bucket_image_path = os.path.join(
            bucket_directory,
            imagename
        )

        image_storage = ImageStorage()

        image_storage.save(bucket_image_path, image_object)
        image.name = imagename
        image.type = image_extension
        image.relative_path = bucket_image_path
        image.absolute_path = image_storage.url(bucket_image_path).split("?")[0]

        image.uploaded = True
        image.save()

        return image