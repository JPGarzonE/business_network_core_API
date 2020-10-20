"""User views."""

# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
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
    UserModelSerializer,
    UserNestedModelSerializer,
    UserSignupSerializer, 
    UserLoginSerializer, 
    AccountVerificationSerializer
)

# Create your views here.

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


    @swagger_auto_schema( operation_id = "Signup", tags = ["Authentication"], request_body = UserSignupSerializer,
        responses = { 201: openapi.Response( "User created", UserModelSerializer, examples = {
                "application/json" : [ {"user": "UserObject", "access_token": "string"} ]
            }), 
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"password_confirmation": ["This field is required"], "company": {"nit": ["company with this nit alredy exist"]},
                "non_field_errors": ["las contraseñas no concuerdan"] }
            ]})
        }, security = [{ "Anonymous": [] }])
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


    @swagger_auto_schema( operation_id = "Login", tags = ["Authentication"], request_body = UserLoginSerializer,
        responses = { 201: openapi.Response( "User authenticated", UserModelSerializer, examples = {
                "application/json" : [ {"user": "UserObject", "access_token": "string"} ]
            }), 
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"non_field_errors": ["Invalid credentials"] }
            ]})
        }, security = [{ "Anonymous": [] }])
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Endpoint for authenticate a user in the system. Return an access_token for grant future access."""
        serializer = UserLoginSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )
        user, token = serializer.save()

        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token
        }
        return Response( data, status = status.HTTP_201_CREATED )

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response."""
        response = super(UserViewSet, self).retrieve(request, *args, **kwargs)

        data = {
            'user': response.data,
            'is_owner': request.user.username == response.data.get("username")
        }

        response.data = data
        return response


class UserIdentityAPIView(APIView):
    """User identity API view that identify and return a 
    user according the access token in the request headers."""

    permission_classes = [IsAuthenticated]

    def get(self, request, format = None, **kwargs):
        """Handle HTTP get for retrieving a user according its access token"""
        serializer = UserNestedModelSerializer( request.user )
        data = serializer.data

        return Response( data, status.HTTP_200_OK)


class AccountVerificationAPIView(APIView):
    """Account verification API view."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request"""

        serializer = AccountVerificationSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        data = {'message': 'Felicitaciones, ¡Ahora ve y haz crecer tu marca!'}

        return Response(data, status = status.HTTP_200_OK)
