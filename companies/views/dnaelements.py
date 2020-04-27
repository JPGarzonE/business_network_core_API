"""Company DNAElements views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Models
from companies.models import Company, Dnaelement, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import DnaelementModelSerializer, CreateCompanyDnaelementSerializer

class DnaelementViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Dnaelement view set"""

    serializer_class = DnaelementModelSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(DnaelementViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['retrieve']:
            permissions = [IsDataOwner]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company Dnaelements"""
        return Dnaelement.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN
        )

    def get_object(self):
        """Return the Dnaelement by the id"""
        dnaelement = get_object_or_404(
            Dnaelement,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN
        )

        return dnaelement

    def perform_destroy(self, instance):
        """Disable Dnaelement."""
        instance.visibility = VisibilityState.DELETED
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Dnaelement creation."""
        dnaelement_serializer = CreateCompanyDnaelementSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        dnaelement_serializer.is_valid(raise_exception = True)
        dnaelement = dnaelement_serializer.save()

        data = self.get_serializer(dnaelement).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(DnaelementViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'dnaelement': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
