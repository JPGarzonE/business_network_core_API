"""Company locations views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Models
from companies.models import Company, Location, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import LocationModelSerializer, CreateCompanyLocationSerializer

class LocationViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Location view set"""

    serializer_class = LocationModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(LocationViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['retrieve']:
            permissions = [IsAuthenticated]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company locations"""
        principal = self.request.query_params.get('principal')
        principal = bool(principal)

        if principal is True:
            return Location.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN,
                principal = True
            )
        else:
            return Location.objects.filter(
                company = self.company,
                visibility = VisibilityState.OPEN
            )

    def get_object(self):
        """Return the location by the id"""
        location = get_object_or_404(
            Location,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN
        )

        return location

    def perform_destroy(self, instance):
        """Disable location."""
        instance.visibility = 'Deleted'
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = LocationModelSerializer(
            instance = instance,
            data=  request.data,
            context = {'company': self.company},
            partial = True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Handle location creation."""
        location_serializer = CreateCompanyLocationSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        location_serializer.is_valid(raise_exception = True)
        location = location_serializer.save()

        data = self.get_serializer(location).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(LocationViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'location': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
