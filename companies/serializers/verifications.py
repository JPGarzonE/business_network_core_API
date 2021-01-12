# Serializers verifications

# Django
from django.db import transaction
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Company, CompanyVerification, CompanyVerificationFile
from multimedia.models import File

# Serializers
from multimedia.serializers.files import FileModelSerializer

# Utilities
from datetime import timedelta
import jwt


# User verification payload type
USER_VERIFICATION_PAYLOAD_TYPE = 'user_email_confirmation'

# Company verification payload type
COMPANY_VERIFICATION_PAYLOAD_TYPE = 'existence_company_confirmation'


def generate_user_verification_token(user):
    """Create JWT token that the user can use to verify its account."""
    payload = {
        'user': user.username,
        'type': USER_VERIFICATION_PAYLOAD_TYPE
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')
    return token.decode()


def validate_user_verification_token(token):
    """Recieves the verification JWT token of a company, 
    validate if its correct and returns the payload."""

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = 'HS256')
    except jwt.ExpiredSignatureError:
        raise serializers.ValidationError('Verification link has expired')
    except jwt.PyJWTError:
        raise serializers.ValidationError('Invalid token')

    if payload['type'] != USER_VERIFICATION_PAYLOAD_TYPE:
        raise serializers.ValidationError('Invalid token')

    return payload


def generate_company_verification_token(company):
    """Create JWT token that the company can use to verify its account."""
    payload = {
        'company': company.accountname,
        'type': COMPANY_VERIFICATION_PAYLOAD_TYPE
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')
    return token.decode()


def validate_company_verification_token(token):
    """Recieves the verification JWT token of a company, 
    validate if its correct and returns the payload."""

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = 'HS256')
    except jwt.ExpiredSignatureError:
        raise serializers.ValidationError('Verification link has expired')
    except jwt.PyJWTError:
        raise serializers.ValidationError('Invalid token')

    if payload['type'] != COMPANY_VERIFICATION_PAYLOAD_TYPE:
        raise serializers.ValidationError('Invalid token')

    return payload


@transaction.atomic
def send_company_verification_notification_email(user, company, certificates_paths):
    token = generate_company_verification_token(company)

    subject = 'NEW verification process has been opened - Conecty API'
    from_email, to_receivers = settings.EMAIL_HOST_USER, ["felipe@joinconecty.com",]

    content = render_to_string(
        'emails/verifications/open_verification_process_notification.html',
        {
            'user': user,
            'company': company,
            'verify_url': "https://joinconecty.com/activate?key={}".format(token),
            'certificates_urls': certificates_paths
        }
    )

    msg = EmailMultiAlternatives(subject, content, from_email, to_receivers)
    msg.attach_alternative(content, "text/html")
    msg.send()


class CompanyVerificationModelSerializer(serializers.ModelSerializer):
    """Company verification model serializer."""

    files = FileModelSerializer(read_only = True, many = True)
    state = serializers.ChoiceField(
        choices = [stateOption.value for stateOption in CompanyVerification.States]
    )

    class Meta:
        """Company verification meta class."""

        model = CompanyVerification

        fields = (
            'id',
            'state',
            'verified',
            'files',
            'application_date',
            'finish_date',
        )

        read_only_fields = (
            'verified',
            'state',
            'application_date',
            'finish_date'
        )


class HandleCompanyVerificationSerializer(serializers.ModelSerializer):
    """Update a company verification."""

    requires_context = True

    files = serializers.ListField(
       child = serializers.IntegerField(),
       help_text = """Array with the ids of the files previously uploaded.
        To upload a file to the platform do it through the Files endpoints."""
    )

    class Meta:
        """Company verification meta class."""

        model = CompanyVerification

        fields = ('files',)


    @transaction.atomic
    def update(self, instance, validated_data):
        """
            Cutomize the update function for the serializer to update the
            related_field values.
        """
        if 'files' in validated_data:
            files = validated_data.pop("files")
            file_objects = []

            for file_id in files:
                file_object = File.objects.get( id = file_id )
                file_objects.append(file_object)

                CompanyVerificationFile.objects.create(
                    company_verification = instance, file = file_object
                )

            instance.state = CompanyVerification.States.INPROGRESS.value
            verification_updated = super().update(instance, validated_data)

            user, company = self.context['user'], self.context['company']
            certificates_urls = [FileModelSerializer().get_path(file_obj) for file_obj in file_objects]

            send_company_verification_notification_email(user, company, certificates_urls)
        
        else:
            verification_updated = super().update(instance, validated_data)

        return verification_updated


class VerifyCompanySerializer(serializers.Serializer):
    """Serializer that recieves the verification token of a company and verify it."""

    token = serializers.CharField(
        help_text = "Verification token that is provided by the `Company Verification Token` endpoint"
    )

    def validate_token(self, data):
        """Verify token is valid."""
        self.context['payload'] = validate_company_verification_token(data)
        return data

    @transaction.atomic
    def save(self):
        """Update company's verified status"""
        payload = self.context['payload']
        company = Company.objects.get(accountname = payload['company'])
        company.is_verified = True
        company.save()

        verification = company.verification
        verification.verified = True
        verification.state = CompanyVerification.States.SUCCESS.value
        verification.finish_date = timezone.now()
        verification.save()