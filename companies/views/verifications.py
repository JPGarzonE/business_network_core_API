# View verifications

# Django
from django.utils.decorators import method_decorator
from django.db import transaction
 
# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from ..permissions import IsCompanyMemberWithEditPermission, IsCompanyMemberWithAdminPermission

# Models
from ..models import Company

# Serializer
from ..serializers import (
    CompanyVerificationModelSerializer, 
    generate_company_verification_token,
    HandleCompanyVerificationSerializer,
    VerifyCompanySerializer 
)


class CompanyVerificationAPIView(APIView):
    """
    Company verification view.
    Handle update and retrieve of the verification of a user.
    """

    permission_classes = [IsAuthenticated, IsCompanyMemberWithAdminPermission]
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verify that the company exists."""
        company_accountname = kwargs['accountname']
        self.company = get_object_or_404(Company, accountname = company_accountname)

        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema( tags = ["Company Verification"], security = [{ "api-key": []}],
        responses = { 200: CompanyVerificationModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} })}
    )
    def get(self, request, format = None):
        """Retrieve Company Verification\n
            Endpoint to retrieve the verification of the company with the account name by url param.
        """
        company_verification = self.get_object(request)

        data = CompanyVerificationModelSerializer( company_verification ).data
        return Response(data, status.HTTP_200_OK)


    @swagger_auto_schema( tags = ["Company Verification"], security = [{ "api-key": [] }],
        request_body = HandleCompanyVerificationSerializer,
        responses = { 200: CompanyVerificationModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request") }
    )
    @transaction.atomic
    def patch(self, request, user_id = None):
        """Upload Company Verification Certificates\n
            Endpoint to upload the verification certificates that are required for verify a company.
        """
        instance = self.get_object(request)

        vertification_serializer = HandleCompanyVerificationSerializer(
            instance = instance,
            data = request.data,
            context = {'user': request.user, 'company': self.company},
            partial = True
        )

        vertification_serializer.is_valid(raise_exception = True)
        verification = vertification_serializer.save()

        data = CompanyVerificationModelSerializer( verification ).data
        data_status = status.HTTP_200_OK

        return Response( data, data_status )


    def get_object(self, request):
        return self.company.verification


class CompanyVerificationTokenAPIView(APIView):
    """Company verification token API view
    
    Retrieve the verification token of a company
    """

    permission_classes = [IsAuthenticated & (IsCompanyMemberWithAdminPermission | IsAdminUser)]

    def dispatch(self, request, *args, **kwargs):
        accountname = kwargs["accountname"]
        self.company = get_object_or_404(Company, accountname = accountname)

        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema( tags = ["Company Verification"], security = [{"api-key": ["User owner or admin required"]}],
        responses = { 200: openapi.Response("OK", examples = {"application/json": 
                {'token': 'token'}} ), 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }) 
        })
    def get(self, request, format = None, **kwargs):
        """Company Verification Token\n
            Endpoint to retrieve the verification token of a company.
            This token is unique for each company and is used for verify the account of that company.\n
            For retrieve this token is required to be the user owner of the company or have admin level permissions.
        """

        data = {
            "token": generate_company_verification_token(self.company)
        }

        return Response(data, status.HTTP_200_OK)

    def get_data_owner_company(self):
        """Return the company owner of the data"""
        return self.company


class VerifyCompanyAPIView(APIView):
    """Verify company API view."""

    permission_classes = [AllowAny]

    @swagger_auto_schema( tags = ["Company Verification"], request_body = VerifyCompanySerializer,
        responses = { 200: openapi.Response("OK", examples = {"application/json": 
                {'detail': 'Felicitaciones, ¡Ahora ve y haz crecer tu marca!'} }), 
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "Verification link has expired"} }),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
    )
    def post(self, request, *args, **kwargs):
        """Verify company\n
            Endpoint to verify a company. This is the last step of the basic verification process.\n
            In the body it has to be passed the verification token and if it is correct, the company is verified.
        """

        serializer = VerifyCompanySerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        data = {'detail': 'Felicitaciones, ¡Ahora ve y haz crecer tu marca!'}

        return Response(data, status = status.HTTP_200_OK)