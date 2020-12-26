# views/unregisterd_companies.py

# Django
from django.utils.decorators import method_decorator

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Seralizers
from companies.serializers import UnregisteredCompanyModelSerializer

# Models
from companies.models import UnregisteredCompany
from django.db.models import Q

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List unregistered companies", tags = ["Unregistered Companies"],
    operation_description = "Endpoint to list all the unregistered companies registered in the platform",
    manual_parameters = [
        openapi.Parameter(name = "name", in_ = openapi.IN_QUERY, type = "String"),
        openapi.Parameter(name = "nit", in_ = openapi.IN_QUERY, type = "String"),
        openapi.Parameter(name = "email", in_ = openapi.IN_QUERY, type = "String")
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve an unregistered company", tags = ["Unregistered Companies"], security = [],
    operation_description = "Endpoint to retrieve an unregistered company by its id.",
    responses = { 200: UnregisteredCompanyModelSerializer, 404: openapi.Response("Not Found")}
))
class UnregisteredCompanyViewSet(mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    "Unregistered Company View set."

    serializer_class = UnregisteredCompanyModelSerializer

    def get_permissions(self):
        """Assign permissions based on actions"""

        if self.action in ['list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return unregistered companies"""
        name = self.request.query_params.get('name')
        nit = self.request.query_params.get('nit')
        email = self.request.query_params.get('email')
        query = None

        if name:
            query = Q(name__iexact = name)
        if nit:
            if query:
                query = query & Q(nit__iexact = nit)
            else:
                query = Q(nit__iexact = nit)
        if email:
            if query:
                query = query & Q(email__iexact = email)
            else:
                query = Q(email__iexact = email)
        
        if query:
            return UnregisteredCompany.objects.filter( query )
        else:
            return UnregisteredCompany.objects.all()


    @swagger_auto_schema( tags = ["Unregistered Companies"], request_body = UnregisteredCompanyModelSerializer,
        responses = { 200: UnregisteredCompanyModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json": {"name": ["This field is required"]} })
        }, security = [{ "api-key": [] }])
    def create(self, request, *args, **kwargs):
        """Create an unregistered company\n
            Endpoint to create an unregistered company.
        """

        unregistered_company_serializer = UnregisteredCompanyModelSerializer(
            data = request.data,
            context = {'company'}
        )

        unregistered_company_serializer.is_valid(raise_exception = True)
        unregistered_company = unregistered_company_serializer.save()

        data = self.get_serializer(unregistered_company).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)
    