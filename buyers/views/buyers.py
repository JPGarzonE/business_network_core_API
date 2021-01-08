# Views buyers

# Constants
from companies.constants import VisibilityState

# Django
from django.utils.decorators import method_decorator

# Django-rest framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import BuyerProfile
 
# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsBuyerMemberWithEditPermission
 
# Serializers
from ..serializers import (
    BuyerProfileModelSerializer, 
    SignupBuyerSerializer
)
from companies.serializers import CompanyModelSerializer


@method_decorator(name = 'list', decorator = swagger_auto_schema( operation_id = "List Buyers", tags = ["Buyers"],
    operation_description = "Endpoint to list all the buyers registered in the platform",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name = 'retrieve', decorator = swagger_auto_schema( 
    operation_id = "Retrieve a buyer", tags = ["Buyers"],
    operation_description = """Endpoint to retrieve the buyer of a company registered in 
        the platform by the company accountname""",
    responses = { 200: BuyerProfileModelSerializer, 404: openapi.Response("Not Found")}, security = []
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class BuyerViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin, 
                    viewsets.GenericViewSet):
    """Buyer view set."""

    serializer_class = BuyerProfileModelSerializer
    lookup_field = 'accountname'
    lookup_value_regex = '[\w.]+'

    def get_queryset(self):
        """Return buyers."""

        return BuyerProfile.objects.filter(
            visibility = VisibilityState.OPEN.value
        )

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['retrieve', 'list', 'signup']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsBuyerMemberWithEditPermission]

        return [permission() for permission in permissions]


    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the buyer)"""
        return self.get_object().company
 

    def get_object(self):
        return get_object_or_404(
            BuyerProfile,
            company__accountname = self.kwargs['accountname'],
            visibility = VisibilityState.OPEN.value
        )

    def perform_destroy(self, instance):
        """Disable membership."""
        instance.visibility = VisibilityState.DELETE.value
        instance.save()

    @swagger_auto_schema( operation_id = "Partial update a buyer", tags = ["Buyers"], request_body = BuyerProfileModelSerializer,
        responses = { 200: BuyerProfileModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"display_name": ["max 60 characters"]}
            })
        }, security = [{ "api-key": [] }]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partial update a buyer model."""
        try:
            instance = self.get_object()
            buyer_serializer = BuyerProfileModelSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            buyer_serializer.is_valid(raise_exception = True)
            buyer = buyer_serializer.save()

            data = self.get_serializer(buyer).data
            data_status = status.HTTP_200_OK
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    

    @swagger_auto_schema( operation_id = "Signup a Buyer", tags = ["Authentication"], request_body = SignupBuyerSerializer,
        responses = { 201: openapi.Response( "Company created", CompanyModelSerializer), 
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"password_confirmation": ["This field is required"], "name": ["There is alredy a company with this name"],
                "non_field_errors": ["las contraseñas no concuerdan"] }
            ]})
        }, security = [{ "Anonymous": [] }]
    )
    @action(detail = False, methods = ['post'])
    def signup(self, request):
        """Endpoint for signup a buyer company with user access in the system.
        It returns the company created and the access_token to access inmediately."""
        serializer = SignupBuyerSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )   
        company, token = serializer.save()

        data = {
            'company': CompanyModelSerializer( company ).data,
            'access_token': token
        }

        return Response( data, status = status.HTTP_201_CREATED )