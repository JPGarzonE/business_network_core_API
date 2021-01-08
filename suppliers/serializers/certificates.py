# Serializers certificates

# Django rest framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Django
from django.db import transaction

# Models
from ..models import Certificate, SupplierCertificate
from multimedia.models import Image
from multimedia.serializers.images import ImageModelSerializer


class CertificateModelSerializer(serializers.ModelSerializer):
    """Certificate model serializer."""

    logo = ImageModelSerializer()

    class Meta:
        """Certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'logo')


class SupplierCertificateModelSerializer(serializers.ModelSerializer):
    """Supplier certificate model serializer."""

    certificate = CertificateModelSerializer()

    class Meta:
        """Supplier Certificate meta class."""

        model = SupplierCertificate

        fields = ('id', 'supplier', 'certificate')


class CreateSupplierCertificateSerializer(serializers.ModelSerializer):
    """Create a supplier certificate. This serializer recieves a 
        certificate id for associate a supplier with an existing 
        certificate OR the data for create a certificate in the same request.
        If both are sent, the certificate_id is going to be first.
    """

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 60,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    description = serializers.CharField(
        max_length = 155,
        required = False,
        allow_null = True,
        allow_blank = True
    )

    logo_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the image (previously uploaded in the platform) that represents the certificate authority"
    )

    certificate_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the certificate (previously created)"
    )

    class Meta:
        """Company certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'logo_id', 'certificate_id')

    
    @transaction.atomic
    def create(self, data):
        """Create a new supplier certificate."""
        supplier = self.context['supplier']
        certificate_id = data.get('certificate_id')

        if certificate_id:
            certificate = get_object_or_404(
                Certificate,
                id = certificate_id
            )
        elif data.get('name') and len(data.get('name')) > 0:
            image = None

            if data.get('logo_id'):
                image_id = data.pop("logo_id")
                try:
                    image = Image.objects.get( id = image_id )
                except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in 'logo_id'" )

            certificate = Certificate.objects.create(**data)

            if image:
                certificate.logo = image
                certificate.save()
        else:
            raise Exception("The body data must have at least a name for the certificate creation or a certificate_id for associating to a existing certificate.")

        supplier_certificate = SupplierCertificate.objects.create(
            supplier = supplier,
            certificate = certificate
        )

        return supplier_certificate


class UpdateCertificateSerializer(serializers.ModelSerializer):
    """Update a certificate."""

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

    logo_id = serializers.IntegerField(
        required = False,
        help_text = "Id of the image previously uploaded in the platform"
    )

    class Meta:
        """certificate meta class."""

        model = Certificate

        fields = ('id', 'name', 'description', 'logo_id')
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Customize the update function for the serializer to update the
            related_field values.
        """
        if 'logo_id' in validated_data:
            logo_id = validated_data.pop('logo_id')
            try:
                logo = Image.objects.get( id = logo_id )
            except Image.DoesNotExist:
                    raise Exception( "Theres no image with the id provided in 'logo_id'" )

            if logo:
                instance.logo = logo

        certificate_updated = super().update(instance, validated_data)

        return certificate_updated