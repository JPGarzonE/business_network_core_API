"""Company services views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Models
from companies.models import Company, Service, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import ServiceModelSerializer, HandleCompanyServiceSerializer

class ServiceViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Service view set"""

    serializer_class = ServiceModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(ServiceViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company services"""
        return Service.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the service by the id"""
        service = get_object_or_404(
            Service,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return service

    def perform_destroy(self, instance):
        """Disable service."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Service creation."""
        service_serializer = HandleCompanyServiceSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        service_serializer.is_valid(raise_exception = True)
        service = service_serializer.save()

        data = self.get_serializer(service).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def partial_update(self, request, *args, **kwargs):
        """Handle product partial update and add a 
        image to a service by its id if its the case"""
        instance = self.get_object()
        service_serializer = HandleCompanyServiceSerializer(
            instance = instance,
            data = request.data,
            partial = True
        )

        service_serializer.is_valid(raise_exception = True)
        service = service_serializer.save()

        data = self.get_serializer(service).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)


class ServiceDetailView(APIView):
    """
        Retrieve the detail of a service.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format = None):
        """Return the service by the id"""
        service = self.get_object(pk)
        serializer = ServiceModelSerializer(service)

        return Response(serializer.data)

    def get_object(self, pk):
        service = get_object_or_404(
            Service,
            id = pk,
            visibility = VisibilityState.OPEN.value
        )

        return service
