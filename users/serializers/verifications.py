"""Verifications serializer."""

# Django
from django.db import transaction
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Company
from users.models import User, Verification
from multimedia.models import Document

# Serializers
from multimedia.serializers.documents import DocumentModelSerializer

# Utilities
from datetime import timedelta
import jwt

def generate_verification_token(user):
    """Create JWT token that the user can use to verify its account."""
    payload = {
        'user': user.username,
        'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')
    return token.decode()


@transaction.atomic
def send_verification_notification_email(user, certificate_path):
    company = Company.objects.get( user = user )
    token = generate_verification_token(user)

    subject = 'NEW verification process has been opened - Conecty API'
    from_email, to_receivers = settings.EMAIL_HOST_USER, ["jgarzonebrath08@gmail.com",]

    content = render_to_string(
        'emails/verifications/open_verification_process_notification.html',
        {
            'user': user,
            'company': company,
            'verify_url': "https://joinconecty.com/activate?key={}".format(token),
            'certificate_url': certificate_path
        }
    )

    msg = EmailMultiAlternatives(subject, content, from_email, to_receivers)
    msg.attach_alternative(content, "text/html")
    msg.send()



class VerificationModelSerializer(serializers.ModelSerializer):
    """Verification model serializer."""

    documents = DocumentModelSerializer(many = True)

    class Meta:
        """Verification meta class."""

        model = Verification

        fields = (
            'id',
            'state',
            'verified',
            'documents',
            'application_date',
            'finish_date',
        )

        read_only_fields = (
            'verified',
            'state',
            'application_date',
            'finish_date'
        )


class HandleVerificationSerializer(serializers.ModelSerializer):
    """Update a verification."""

    requires_context = True

    documents = serializers.ListField(
       child = serializers.IntegerField()
    )

    class Meta:
        """Verification meta class."""

        model = Verification

        fields = (
            'id',
            'state',
            'verified',
            'documents',
            'application_date',
            'finish_date',
        )

        read_only_fields = (
            'verified',
            'state',
            'application_date',
            'finish_date'
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        if 'documents' in validated_data:
            documents = validated_data.pop("documents")

            for document_id in documents:
                document_object = Document.objects.get( id = document_id )
                document_object.verification = instance
                document_object.save()

            instance.state = "InProgress"
            verification_updated = super().update(instance, validated_data)

            user = self.context['user']
            document_path = DocumentModelSerializer().get_path(document_object)

            send_verification_notification_email(user, document_path)
        
        else:
            verification_updated = super().update(instance, validated_data)

        return verification_updated