"""Documents serializer."""

import os

# Django rest framework
from rest_framework import serializers

# Django
from django.db import transaction

# Models
from users.models import User
from multimedia.models import Document

# Storages
from multimedia.storages import FileStorage

class DocumentModelSerializer(serializers.ModelSerializer):
    """Document model serializer."""

    path = serializers.SerializerMethodField()

    class Meta:
        """Document meta class."""

        model = Document

        fields = (
            'id',
            'user',
            'name',
            'path',
            'purpose',
            'type',
            'size',
            'valid',
            'created_date',
            'uploaded'
        )

        read_only_fields = (
            'id',
            'path',
            'purpose',
            'type',
            'size',
            'valid',
            'created_date',
            'uploaded'
        )

    def get_path(self, instance):
        file_storage = FileStorage()
        file_path = instance.relative_path

        return file_storage.url(file_path)


class CreateDocumentSerializer(serializers.Serializer):
    """
    Serializer in charge of creating the document in the bucket 
    and in the database
    """

    requires_context = True

    file = serializers.FileField(required = True, allow_empty_file = False)

    purpose = serializers.CharField(
        help_text = "Describes the need that the document meets. Ej: Company comercial certificate",
        max_length = 50,
        required = True
    )

    @transaction.atomic
    def create(self, data):
        """Create and store a new document"""
        user = self.context['user']
        file_object = data.get("file")
        purpose = data.get("purpose")

        file_size = file_object.size # size in bytes

        document = Document.objects.create(
            user = user,
            name = file_object.name,
            size = file_size,
            purpose = purpose
        )
        document_id = document.id

        bucket_directory = '{username}/{file_object_id}/'.format( 
            username = user.username,
            file_object_id = document_id
        )

        _, file_extension = os.path.splitext(file_object.name)
        
        filename = '{file_object_id}{file_extension}'.format(
            file_object_id = document_id,
            file_extension = file_extension
        )
        
        bucket_file_path = os.path.join(
            bucket_directory,
            filename
        )

        file_storage = FileStorage()

        if not file_storage.exists(bucket_file_path):
            file_storage.save(bucket_file_path, file_object)
            document.type = file_extension
            document.relative_path = bucket_file_path
            document.absoulte_path = file_storage.url(bucket_file_path).split("?")[0]
            document.path = file_storage.url(bucket_file_path)
            document.uploaded = True
            document.save()

            return document
        else:
            raise Exception("File {filename} alredy exists for the user {username} in bucket {bucket_name}".format(
                filename = file_object.name,
                username = user.username,
                bucket_name = file_storage.bucket_name
            ))