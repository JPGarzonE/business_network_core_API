"""Media serializer."""

import os

# Django rest framework
from rest_framework import serializers

# Django
from django.core.files.images import get_image_dimensions
from django.db import transaction

# Models
from users.models import User
from multimedia.models import Media

# Storages
from multimedia.storages import VideoStorage, ImageStorage

class MediaModelSerializer(serializers.ModelSerializer):
    """Media model serializer."""

    path = serializers.SerializerMethodField()

    class Meta:
        """Media meta class."""

        model = Media

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
        image_storage = ImageStorage()
        image_path = instance.relative_path
        print("Entra")
        print(image_path)
        return image_storage.url(image_path)

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
        image_object = data.get("image")
        
        image_size = image_object.size # size in bytes
        image_width = get_image_dimensions(image_object)[0]
        image_height = get_image_dimensions(image_object)[1]

        _, image_extension = os.path.splitext(image_object.name)

        image = Media.objects.create(
            width = image_width,
            height = image_height,
            size = image_size,
            type = image_extension
        )
        image_id = image.id

        bucket_directory = '{username}/{image_object_id}/'.format( 
            username = self.context['user'],
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

        if not image_storage.exists(bucket_image_path):
            image_storage.save(bucket_image_path, image_object)
            image.name = imagename
            image.type = image_extension
            image.relative_path = bucket_image_path
            image.absolute_path = image_storage.url(bucket_image_path).split("?")[0]
            print("image")
            print(image.absolute_path)
            image.uploaded = True
            image.save()

            return image
        else:
            raise Exception("File {imagename} alredy exists for the user {username} in bucket {bucket_name}".format(
                imagename = image_object.name,
                username = self.context['user'],
                bucket_name = image_storage.bucket_name
            ))