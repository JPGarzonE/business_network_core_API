"""Company contacts views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Models
from companies.models import Company, Contact, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner, IsCompanyAccountOwnerOrIsVerified

# Serializers
from companies.serializers import ContactModelSerializer, HandleCompanyContactSerializer

# Utils
from distutils.util import strtobool

class ContactViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Contact view set."""

    serializer_class = ContactModelSerializer
    company = None

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
        principal = self.request.query_params.get('principal')
        

        if principal:
            principal = bool( strtobool(principal) )

            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value,
                principal = principal
            )
        else:
            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN.value
            )

    def list(self, request, *args, **kwargs):
        """Valid param principal before super list eventually executes get_queryset method"""
        principal = self.request.query_params.get('principal')

        if principal:
            try:
                bool( strtobool(principal) )
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

    def create(self, request, *args, **kwargs):
        """Handle contact creation."""
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

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(ContactViewSet, self).retrieve(request, *args, **kwargs)

        data = response.data
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
