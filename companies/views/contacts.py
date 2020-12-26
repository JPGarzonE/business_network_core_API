"""Company contacts views."""

# Django
from django.utils.decorators import method_decorator

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company, Contact, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner, IsCompanyAccountOwnerOrIsVerified

# Serializers
from companies.serializers import ContactModelSerializer, HandleCompanyContactSerializer

# Utils
from distutils.util import strtobool


@method_decorator( name = 'destroy', decorator = swagger_auto_schema( operation_id = "Delete a company contact", tags = ["Supplier Contacts"],
    operation_description = "Endpoint to delete a company contact by its id",
    responses = { 204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }, security = [{ "api-key": [] }]
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class ContactViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Contact view set."""

    serializer_class = ContactModelSerializer
    company = None
    principal_contact = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(ContactViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [IsAuthenticated, IsCompanyAccountOwnerOrIsVerified]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company contacts"""
        principal = self.principal_contact if self.principal_contact else None
        principal_contact_id = self.company.principal_contact.id if self.company.principal_contact else None

        if principal is True:
            return Contact.objects.filter( 
                id = principal_contact_id
            )

        elif principal is False:
            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value
            ).exclude( id = principal_contact_id )

        else:
            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value
            )

    @swagger_auto_schema( operation_id = "List company contacts", tags = ["Supplier Contacts"],
        operation_description = "Endpoint to list all the contacts of a company user",
        responses = { 404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
    )
    def list(self, request, *args, **kwargs):
        """Valid param principal before super list eventually executes get_queryset method"""
        principal = self.request.query_params.get('principal')

        if principal:
            try:
                self.principal_contact = bool( strtobool(principal) )
            except ValueError:
                data = {"detail": "Query param 'principal' must be a boolean value"}
                return Response(data, status = status.HTTP_400_BAD_REQUEST)

        return super(ContactViewSet, self).list(request, *args, **kwargs)


    def get_object(self):
        """Return the contact by the id"""
        contact = get_object_or_404(
            Contact,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return contact

    def perform_destroy(self, instance):
        """Disable contact."""
        instance.visibility = 'Deleted'
        instance.save()


    @swagger_auto_schema( tags = ["Supplier Contacts"], request_body = HandleCompanyContactSerializer,
        responses = { 200: ContactModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"email": ["min_length 7 characters"]} 
            })
        }, security = [{ "api-key": [] }])
    def create(self, request, *args, **kwargs):
        """Create company contact\n
            Endpoint to create a contact of a company with the username provided    
        """
        try:
            contact_serializer = HandleCompanyContactSerializer(
                data = request.data,
                context = {'company': self.company}
            )

            contact_serializer.is_valid(raise_exception = True)
            contact = contact_serializer.save()

            data = self.get_serializer(contact).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)


    @swagger_auto_schema( operation_id = "Partial update company contact", tags = ["Supplier Contacts"], request_body = HandleCompanyContactSerializer,
        responses = { 200: ContactModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"email": ["min_length 7 characters"]}
            })
        }, security = [{ "api-key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Endpoint to update partially a contact object. It is partial, so its not needed pass all the body values"""
        try:
            instance = self.get_object()
            serializer = HandleCompanyContactSerializer(
                instance = instance,
                data=  request.data,
                context = {'company': self.company},
                partial = True
            )
            serializer.is_valid(raise_exception=True)
            contact = serializer.save()

            data = self.get_serializer(contact).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST

        return Response(data, status = data_status)


    @swagger_auto_schema( operation_id = "Retrieve a company contact", tags = ["Supplier Contacts"],
        operation_description = "Endpoint to retrieve a contact owned by a company according its id.",
        responses = { 200: ContactModelSerializer, 404: openapi.Response("Not Found")}, security = [{ "api-key": [] }]
    )
    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(ContactViewSet, self).retrieve(request, *args, **kwargs)

        data = response.data
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
