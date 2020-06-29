# views/unregisterd_companies.py

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Seralizers
from companies.serializers import UnregisteredCompanyModelSerializer

# Models
from companies.models import UnregisteredCompany
from django.db.models import Q

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


class UnregisteredCompanyViewSet(mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    "Unregistered Company View set."

    serializer_class = UnregisteredCompanyModelSerializer

    def get_permissions(self):
        """Assign permissions based on actions"""

        if self.action in ['list']:
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

    def create(self, request, *args, **kwargs):
        """Handle unregistered company creation"""
        unregistered_company_serializer = UnregisteredCompanyModelSerializer(
            data = request.data,
            context = {'company'}
        )

        unregistered_company_serializer.is_valid(raise_exception = True)
        unregistered_company = unregistered_company_serializer.save()

        data = self.get_serializer(unregistered_company).data
        data_status = status.HTTP_201_CREATED

        return Response(data, status = data_status)
    