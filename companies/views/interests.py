"""Company Interest views."""

# Django
from django.utils.decorators import method_decorator

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from companies.models import Company, Interest, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import InterestModelSerializer, CreateCompanyInterestSerializer


@method_decorator(name = 'list', decorator = swagger_auto_schema( operation_id = "List company interests", tags = ["Company Interests"],
    operation_description = "Endpoint to list all the interests that has a company",
    responses = { 404: openapi.Response("Not Found") }, security = [{"api-key": []}]
))
@method_decorator(name = 'update', decorator = swagger_auto_schema(auto_schema = None) )
@method_decorator(name = 'partial_update', decorator = swagger_auto_schema( 
    operation_id = "Partial update a company interest", tags = ["Company Interests"], 
    operation_description = "Endpoint to partial update a company interest by company username and interest id.",
    responses = { 404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
))
@method_decorator(name = 'destroy', decorator = swagger_auto_schema(
    operation_id = "Delete a company interest", tags = ["Company Interests"], security = [{ "api-key": [] }],
    operation_description = "Endpoint to delete a company interest by company username and interest id",
    responses = { 
        204: openapi.Response("No Content"), 404: openapi.Response("Not Found"),
        401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
    }
))
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


    @swagger_auto_schema( tags = ["Company Interests"], request_body = CreateCompanyInterestSerializer,
        responses = { 
            200: InterestModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = { "application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json": {"name": ["This field is required"]} })
        }, security = [{"api-key": []}]
    )
    def create(self, request, *args, **kwargs):
        """Create a company interest\n
            Endpoint to create an interest for a company by the username given.
        """

        interest_serializer = CreateCompanyInterestSerializer(
            data = request.data,
            context = {'company': self.company}
        )
        interest_serializer.is_valid(raise_exception = True)
        interest = interest_serializer.save()

        data = self.get_serializer(interest).data
        data_status = status.HTTP_201_CREATED
        
        return Response(data, status = data_status)


    @swagger_auto_schema( tags = ["Company Interests"], security = [{"api-key": []}],
        responses = { 200: InterestModelSerializer, 404: openapi.Response("Not Found") }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a company interest\n
            Endpoint to retrieve a company interest by company username and interest id.
        """

        response = super(InterestViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'interest': response.data
        }
        data_status = status.HTTP_200_OK

        return Response( data, status = data_status )
