# views/companies.py

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema

# Serializers
from companies.serializers import (
    CompanyModelSerializer, UpdateCompanySerializer, 
    CompanySummarySerializer, UpdateCompanySummarySerializer
)

# Models
from companies.models import Company, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Create your views here.

class CompanyViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin, 
                    viewsets.GenericViewSet):
    """Company view set."""

    serializer_class = CompanyModelSerializer
    lookup_field = 'username'
    lookup_value_regex = '[\w.]+'

    def get_queryset(self):
        """Return companies"""
        name = self.request.query_params.get('name')
        nit = self.request.query_params.get('nit')
        company_filter = None

        if name and nit:
            company_filter = Company.objects.filter(
                name__iexact = name,
                nit__iexact = nit
            )
        elif name:
            company_filter = Company.objects.filter(
                name__iexact = name
            )
        elif nit:
            company_filter = Company.objects.filter(
                nit__iexact = nit
            )
        else:
            company_filter = Company.objects.all()

        return company_filter.exclude( visibility = VisibilityState.DELETED.value )

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.get_object()

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve', 'list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]

        return [permission() for permission in permissions]

    def get_object(self):
        company = get_object_or_404(
            Company,
            user__username = self.kwargs['username'],
            visibility = VisibilityState.OPEN.value
        )
        self.company = company
        
        return company

    def perform_destroy(self, instance):
        """Disable membership."""
        instance.visibility = VisibilityState.DELETE.value
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        """Handle company partial update and add a 
        image to a company logo by its id if its the case"""
        try:
            instance = self.get_object()
            company_serializer = UpdateCompanySerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            company_serializer.is_valid(raise_exception = True)
            company = company_serializer.save()

            data = self.get_serializer(company).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)


class CompanySummaryViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, 
                            viewsets.GenericViewSet):
    """View set of the main summary of the company"""

    serializer_class = CompanySummarySerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username, 
            visibility = VisibilityState.OPEN.value)

        return super(CompanySummaryViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        
        return [permission() for permission in permissions]

    def get_queryset(self):
        username = self.kwargs['username']
        return get_object_or_404(Company, user__username = username)

    def get_object(self):
        return self.company

    def partial_update(self, request, *args, **kwargs):
        """Handle company partial update and add a 
        image to a company logo by its id if its the case"""
        try:
            instance = self.get_object()
            company_serializer = UpdateCompanySummarySerializer(
                instance = instance,
                data = request.data,
                context = {"company": self.company},
                partial = True
            )

            company_serializer.is_valid(raise_exception = True)
            company = company_serializer.save()

            data = self.get_serializer(company).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)