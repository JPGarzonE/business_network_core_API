# Serializer files

# OS
import os

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from multimedia.models import File

# Storages
from multimedia.storages import FileStorage


def serialize_file_relative_path(file_relative_path):
    """Method that take the relative path of an uploaded 
    file in s3 and returns the signed path for that file."""

    file_storage = FileStorage()

    return file_storage.url(file_relative_path)


class FileModelSerializer(serializers.ModelSerializer):
    """File model serializer."""

    path = serializers.SerializerMethodField()

    class Meta:
        """Document meta class."""

        model = File

        fields = (
            'id',
            'name',
            'path',
            'type',
            'size',
            'created_date',
            'uploaded'
        )

        read_only_fields = (
            'id',
            'path',
            'type',
            'size',
            'created_date',
            'uploaded'
        )

    def get_path(self, instance):
        file_path = instance.relative_path

        return serialize_file_relative_path(file_path)


class CreateFileSerializer(serializers.Serializer):
    """
    Serializer in charge of creating the document in the bucket 
    and in the database
    """

    requires_context = True

    file = serializers.FileField(required = True, allow_empty_file = False)

    @transaction.atomic
    def create(self, data):
        """Create and store a new file"""

        # Define an appropiate folder name
        request = self.context.get('request')
        company_accountname = request.auth.payload.get('company_accountname')
        username = request.user.username
        folder_name = company_accountname if company_accountname else username

        file_object = data.get("file")
        file_size = file_object.size # size in bytes

        file = File.objects.create(
            name = file_object.name,
            size = file_size
        )
        file_id = file.id

        bucket_directory = '{folder_name}/{file_object_id}/'.format( 
            folder_name = folder_name,
            file_object_id = file_id
        )

        _, file_extension = os.path.splitext(file_object.name)
        
        filename = '{file_object_id}{file_extension}'.format(
            file_object_id = file_id,
            file_extension = file_extension
        )
        
        bucket_file_path = os.path.join(
            bucket_directory,
            filename
        )

        file_storage = FileStorage()

        if not file_storage.exists(bucket_file_path):
            file_storage.save(bucket_file_path, file_object)
            file.type = file_extension
            file.relative_path = bucket_file_path
            file.absoulte_path = file_storage.url(bucket_file_path).split("?")[0]
            file.path = file_storage.url(bucket_file_path)
            file.uploaded = True
            file.save()

            return file
        else:
            raise Exception("File {filename} alredy exists in the folder '{folder_name}' in bucket {bucket_name}".format(
                filename = file_object.name,
                folder_name = folder_name,
                bucket_name = file_storage.bucket_name
            ))