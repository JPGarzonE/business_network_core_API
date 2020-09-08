"""Company Interest views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Models
from companies.models import Company, Interest, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import InterestModelSerializer, CreateCompanyInterestSerializer

class InterestViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Interest view set"""

    serializer_class = InterestModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(InterestViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list', 'retrieve']:
            permissions = [IsAuthenticated]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company Interests"""
        return Interest.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the Interest by the id"""
        interest = get_object_or_404(
            Interest,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return interest

    def perform_destroy(self, instance):
        """Disable Interest."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Interest creation."""
        interest_serializer = CreateCompanyInterestSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        interest_serializer.is_valid(raise_exception = True)
        interest = interest_serializer.save()

        data = self.get_serializer(interest).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(InterestViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'interest': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
