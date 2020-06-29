# companies/views/unregistered_relationships.py

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

# Errors
from django.db.utils import IntegrityError

# Models
from companies.models import Company, UnregisteredRelationship, UnregisteredCompany

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsUnregisteredRelationOwner

# Seralizers
from companies.serializers import UnregisteredRelationshipModelSerializer, CreateUnregisteredRelationshipSerializer


    
class UnregisteredRelationshipViewSet(mixins.CreateModelMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    viewsets.GenericViewSet):
    """Unregistered Relationship view set."""

    queryset = UnregisteredRelationship.objects.all()
    serializer_class = UnregisteredRelationshipModelSerializer

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated]
        else:
            permissions = [IsAuthenticated, IsUnregisteredRelationOwner]

        return [permission() for permission in permissions]

    def create(self, request, *args, **kwargs):
        """Handle unregistered relationship creation"""
        self.company = Company.objects.get( user = request.user )

        unregistered_relationship_serializer = CreateUnregisteredRelationshipSerializer(
            data = request.data,
            context = {"requester": self.company}
        )

        unregistered_relationship_serializer.is_valid(raise_exception = True)
        try:
            unregistered_relationship = unregistered_relationship_serializer.save()
            data = self.get_serializer(unregistered_relationship).data
            data_status = status.HTTP_201_CREATED
        except IntegrityError:
            data = {
                'detail': 'Error. This relationship alredy exist.'
            }
            data_status = status.HTTP_409_CONFLICT
        
        return Response(data, status = data_status)


class ListUnregisteredRelationships(ListAPIView):
    """API view to list all Unregistered Relationships of a user"""

    serializer_class = UnregisteredRelationshipModelSerializer

    def get_queryset(self):
        """Return company unregistered relationship objects"""
        return UnregisteredRelationship.objects.filter(
            requester = self.company
        )
    
    def list(self, request, *args, **kwargs):
        """Handel the list event."""   
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(ListUnregisteredRelationships, self).list(request, *args, **kwargs)
        
    

