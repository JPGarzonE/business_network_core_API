
# Django
from django.shortcuts import render

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Serializers
from companies.serializers import CompanyModelSerializer, UpdateCompanySerializer

# Models
from companies.models import Company, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner

# Create your views here.

class CompanyViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin, 
                    viewsets.GenericViewSet):
    """Company view set."""
    
    queryset = Company.objects.all().order_by('user__username')
    serializer_class = CompanyModelSerializer
    lookup_field = 'username'
    lookup_value_regex = '[\w.]+'


    def get_queryset(self):
        """Return companies"""
        name = self.request.query_params.get('name')
        nit = self.request.query_params.get('nit')
        company_filter = Company.objects.all()

        if name and nit:
            company_filter = Company.objects.filter(
                name = name,
                nit = nit
            )
        elif name:
            company_filter = Company.objects.filter(
                name = name
            )
        elif nit:
            company_filter = Company.objects.filter(
                nit = nit
            )

        return company_filter.exclude( visibility = VisibilityState.DELETED )

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
            visibility = VisibilityState.OPEN
        )
        self.company = company
        
        return company

    def perform_destroy(self, instance):
        """Disable membership."""
        instance.visibility = 'Deleted'
        instance.save()

    def partial_update(self, request, *args, **kwargs):
        """Handle company partial update and add a 
        media to a company logo by its id if its the case"""
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
        
        return Response(data, status = data_status)

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(CompanyViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'company': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )