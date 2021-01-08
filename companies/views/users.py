# Views users

# Django
from django.utils.decorators import method_decorator

# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

# Models
from ..models import User, CompanyMember

# Serializer
from ..serializers import (
    DocumentationUserSerializer,
    UserModelSerializer,
    UserAccessSerializer,
    UserLoginSerializer
)


@method_decorator( name = 'list', decorator = swagger_auto_schema(
    operation_id = "List all users", tags = ["Users"],
    operation_description = "Endpoint to list all the users registered in the platform",
    manual_parameters = [
        openapi.Parameter(name = "email", in_ = openapi.IN_QUERY, type = "String",
            description = "Param for get a user by its email. (This field evaluates an exact match)")
    ],
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator( name = 'retrieve', decorator = swagger_auto_schema(
    operation_id = "Retrieve a user", tags = ["Users"], security = [],
    operation_description = "Endpoint to retrieve a user by its username.",
    responses = { 200: UserModelSerializer, 404: openapi.Response("Not Found") }
))
class UserViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):
    """User view set.

    Handle sign up, login and account verification.
    """
    
    queryset = User.objects.filter(is_active=True, is_client=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'
    lookup_value_regex = '[\w.]+'

    def get_permissions(self):
        """Assign permissions based on actions"""
        if self.action in ['list', 'retrieve', 'login']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return users"""
        email = self.request.query_params.get('email')

        if email:
            return User.objects.filter(
                email = email,
                is_active = True
            )

        return User.objects.filter(
            is_active = True
        )


    @swagger_auto_schema( tags = ["Authentication"], request_body = UserLoginSerializer,
        responses = { 201: openapi.Response( "User authenticated", DocumentationUserSerializer),
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"non_field_errors": ["Invalid credentials"] }
            ]} )}, security = []
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """User Login\n
            Endpoint for authenticate a user in the system. \n
            Return an access_token for grant future access and
            a user object
        """

        serializer = UserLoginSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )
        user, token = serializer.save()

        user_companies = self.get_user_companies(user)

        user_serializer = UserAccessSerializer(
            user = user,
            default_company = user_companies[:1].company,
            other_companies = user_companies[1:]
        )

        data = {
            'access_token': token,
            'access_user': user_serializer.data
        }
        return Response( data, status = status.HTTP_201_CREATED )

    def get_user_companies(self, user):
        """Return all the company memberships that have the user by param."""
        return CompanyMember.objects.filter(user = user)


class UserIdentityAPIView(APIView):
    """User identity API view that identify and return a 
    user according the access token in the request headers 
    and all the companies where the user have access."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema( operation_id = "Me", tags = ["Me"], security = [{ "api-key": []}],
        operation_description = """
            Special endpoint that takes the access token of the request, 
            identify the userof that access token and return the respective 
            user with all the companies where the user have access.""",
        responses = { 200: UserAccessSerializer, 404: openapi.Response("Not Found")}
    )
    def get(self, request, format = None, **kwargs):
        """Handle HTTP get for retrieving a user according its access token"""
        user_companies = self.get_user_companies(request.user)

        serializer = UserAccessSerializer(
            user = request.user,
            default_company = user_companies[:1].company,
            other_companies = user_companies[1:]
        )

        data = serializer.data

        return Response( data, status.HTTP_200_OK)

    def get_user_companies(self, user):
        """Return all the company memberships that have the user by param."""
        return CompanyMember.objects.filter(user = user)
