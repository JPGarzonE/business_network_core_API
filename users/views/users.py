"""User views."""

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
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from users.permissions import IsAccountOwner

# Models
from users.models import User

# Serializer
from users.serializers import (
    DocumentationUserSerializer,
    UserModelSerializer,
    UserNestedModelSerializer,
    UserSignupSerializer, 
    UserLoginSerializer, 
    AccountVerificationSerializer
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
        if self.action in ['signup', 'login', 'list', 'retrieve']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsAccountOwner]

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


    @swagger_auto_schema( operation_id = "Signup", tags = ["Authorization"], request_body = UserSignupSerializer,
        responses = { 201: openapi.Response( "User created", DocumentationUserSerializer), 
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"password_confirmation": ["This field is required"], "company": {"nit": ["company with this nit alredy exist"]},
                "non_field_errors": ["las contraseñas no concuerdan"] }
            ]})
        }, security = [{ "Anonymous": [] }]
    )
    @action(detail = False, methods = ['post'])
    def signup(self, request):
        """Endpoint for signup a user in the system.
        It returns the user created and the access_token to access inmediately."""
        serializer = UserSignupSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )   
        user, token = serializer.save()

        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }

        return Response( data, status = status.HTTP_201_CREATED )


    @swagger_auto_schema( tags = ["Authorization"], request_body = UserLoginSerializer,
        responses = { 201: openapi.Response( "User authenticated", DocumentationUserSerializer),
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"non_field_errors": ["Invalid credentials"] }
            ]} )}, security = []
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login\n
            Endpoint for authenticate a user in the system. Return an access_token for grant future access.\n
        """

        serializer = UserLoginSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )
        user, token = serializer.save()

        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }
        return Response( data, status = status.HTTP_201_CREATED )


class UserIdentityAPIView(APIView):
    """User identity API view that identify and return a 
    user according the access token in the request headers."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema( operation_id = "Me", tags = ["Me"], security = [{ "api-key": []}],
        operation_description = """
            Special endpoint that takes the access token of the request, identify the user
            of that access token and return the respective user.""",
        responses = { 200: UserNestedModelSerializer, 404: openapi.Response("Not Found")}
    )
    def get(self, request, format = None, **kwargs):
        """Handle HTTP get for retrieving a user according its access token"""
        
        serializer = UserNestedModelSerializer( request.user )
        data = serializer.data

        return Response( data, status.HTTP_200_OK)


class AccountVerificationAPIView(APIView):
    """Account verification API view."""

    permission_classes = [AllowAny]

    @swagger_auto_schema( tags = ["User Verifications"], request_body = AccountVerificationSerializer,
        responses = { 200: openapi.Response("OK", examples = {"application/json": 
                {'detail': 'Felicitaciones, ¡Ahora ve y haz crecer tu marca!'} }), 
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "Verification link has expired"} }),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            404: openapi.Response("Not Found") }, security = [{ "api-key": [] }]
    )
    def post(self, request, *args, **kwargs):
        """Verify account\n
            Endpoint to verify the account of a user. This is the last step of the basic verification process.\n
            In the body it has to be passed the verification token and if it is correct, the user account is verified.
        """

        serializer = AccountVerificationSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        data = {'detail': 'Felicitaciones, ¡Ahora ve y haz crecer tu marca!'}

        return Response(data, status = status.HTTP_200_OK)
