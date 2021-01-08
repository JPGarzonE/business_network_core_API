# Views companies

# Constants
from ..constants import VisibilityState

# Django
from django.utils.decorators import method_decorator

# Django rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import Company

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsCompanyMemberWithEditPermission

# Serializers
from ..serializers import CompanyModelSerializer, UpdateCompanySerializer


@method_decorator(name = 'list', decorator = swagger_auto_schema( operation_id = "List companies", tags = ["Companies"],
    operation_description = "Endpoint to list all the companies registered in the platform",
    manual_parameters = [
        openapi.Parameter(name = "name", in_ = openapi.IN_QUERY, type = "String"),
        openapi.Parameter(name = "legal_identifier", in_ = openapi.IN_QUERY, type = "String")
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name = 'retrieve', decorator = swagger_auto_schema( operation_id = "Retrieve a company", tags = ["Companies"],
    operation_description = "Endpoint to retrieve a company registered in the platform",
    responses = { 200: CompanyModelSerializer, 404: openapi.Response("Not Found")}, security = []
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class CompanyViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin, 
                    viewsets.GenericViewSet):
    """Company view set."""

    serializer_class = CompanyModelSerializer
    lookup_field = 'accountname'
    lookup_value_regex = '[\w.]+'

    def get_queryset(self):
        """Return companies"""
        name = self.request.query_params.get('name')
        legal_identifier = self.request.query_params.get('legal_identifier')
        company_filter = None

        if name and legal_identifier:
            company_filter = Company.objects.filter(
                name__iexact = name,
                legal_identifier__iexact = legal_identifier
            )
        elif name:
            company_filter = Company.objects.filter(
                name__iexact = name
            )
        elif legal_identifier:
            company_filter = Company.objects.filter(
                legal_identifier__iexact = legal_identifier
            )
        else:
            company_filter = Company.objects.all()

        return company_filter.exclude( visibility = VisibilityState.DELETED.value )

    def get_data_owner_company(self):
        """Return the company owner of the data."""
        return self.get_object()

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve', 'list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsCompanyMemberWithEditPermission]

        return [permission() for permission in permissions]

    def get_object(self):
        return get_object_or_404(
            Company,
            accountname = self.kwargs['accountname'],
            visibility = VisibilityState.OPEN.value
        )

    def perform_destroy(self, instance):
        """Disable membership."""
        instance.visibility = VisibilityState.DELETE.value
        instance.save()

    @swagger_auto_schema( operation_id = "Partial update a company", tags = ["Companies"], request_body = UpdateCompanySerializer,
        responses = { 200: CompanyModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["This field must be unique"]}
            })
        }, security = [{ "api-key": [] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Handle company partial update and add a 
        image to a company logo by its id if its the case"""
        try:
            instance = self.get_object()
            company_serializer = UpdateCompanySerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            company_serializer.is_valid(raise_exception = True)
            company = company_serializer.save()

            data = self.get_serializer(company).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)