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
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import ContactModelSerializer, CreateContactSerializer

class ContactViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Contact view set."""

    serializer_class = ContactModelSerializer

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
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company contacts"""
        principal = self.request.query_params.get('principal')
        principal = bool(principal)

        if principal is True:
            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN,
                principal = True
            )
        else:
            return Contact.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN
            )

    def get_object(self):
        """Return the contact by the id"""
        contact = get_object_or_404(
            Contact,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN
        )

        return contact

    def perform_destroy(self, instance):
        """Disable contact."""
        instance.visibility = 'Deleted'
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle contact creation."""
        contact_serializer = CreateContactSerializer(
            data = request.data,
            context = {'company': self.company}
        )

        contact_serializer.is_valid(raise_exception = True)
        contact = contact_serializer.save()

        data = self.get_serializer(contact).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(ContactViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'contact': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
