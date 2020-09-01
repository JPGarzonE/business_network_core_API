"""Certificate serializers"""

# Django rest framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Django
from django.db import transaction

# Models
from companies.models import Certificate, CompanyCertificate
from multimedia.models import Media
from multimedia.serializers.media import MediaModelSerializer


class CertificateModelSerializer(serializers.ModelSerializer):
    """Certificate model serializer."""

    image = MediaModelSerializer()

    class Meta:
        """Certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'image')


class CompanyCertificateModelSerializer(serializers.ModelSerializer):
    """Company certificate model serializer."""

    certificate = CertificateModelSerializer()

    class Meta:
        """Certificate meta class."""

        model = CompanyCertificate

        fields = ('id', 'company', 'certificate')


class CreateCompanyCertificateSerializer(serializers.ModelSerializer):
    """Create a company certificate."""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 60,
        required = False
    )

    description = serializers.CharField(
        max_length = 155,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    image_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the image previously uploaded in the platform"
    )

    certificate_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the certificate previously created"
    )

    class Meta:
        """Company certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'image_id', 'certificate_id')

    
    @transaction.atomic
    def create(self, data):
        """Create new company certificate."""
        company = self.context['company']
        certificate_id = data.get('certificate_id')

        if certificate_id:
            certificate = get_object_or_404(
                Certificate,
                id = certificate_id
            )
        elif data.get('name'):
            image = None

            if data.get('image_id'):
                image_id = data.pop("image_id")
                image = Media.objects.get( id = image_id )

            certificate = Certificate.objects.create(**data)

            if image:
                certificate.image = image
                certificate.save()
        else:
            raise Exception("The body data must have at least a name for the certificate creation or a certificate_id for associating to a existing certificate.")

        company_certificate = CompanyCertificate.objects.create(
            company = company,
            certificate = certificate
        )

        return company_certificate


class UpdateCertificateSerializer(serializers.ModelSerializer):
    """Update a company certificate."""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 60
    )

    description = serializers.CharField(
        max_length = 155,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    image_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the image previously uploaded in the platform"
    )

    class Meta:
        """Company certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'image_id')
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Customize the update function for the serializer to update the
            related_field values.
        """
        image = None

        if 'image_id' in validated_data:
            image_id = validated_data.pop('image_id')
            image = Media.objects.get( id = image_id )

            if image:
                instance.image = image

        certificate_updated = super().update(instance, validated_data)

        return certificate_updated