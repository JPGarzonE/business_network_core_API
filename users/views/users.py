"""User views."""

# Django REST Framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from users.permissions import IsAccountOwner

# Models
from users.models import User
from companies.models import Company

# Serializer
from users.serializers import UserModelSerializer, UserSignupSerializer, UserLoginSerializer
from companies.serializers import CompanyModelSerializer

# Create your views here.

class UserViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin, 
                mixins.UpdateModelMixin, 
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
        if self.action in ['signup', 'login', 'retrieve', 'list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsAccountOwner]

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return companies"""
        return User.objects.filter(
            is_active = True
        )

    @action(detail = False, methods = ['post'])
    def signup(self, request):
        """User signup."""
        serializer = UserSignupSerializer( data = request.data )
        serializer.is_valid( raise_exception = True )
        
        user = serializer.save()
        data = UserModelSerializer(user).data

        return Response( data, status = status.HTTP_201_CREATED )

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login."""
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

        user = User.objects.filter(
            username = kwargs.get('username')
        )

        data = {
            'user': response.data
        }

        response.data = data
        return response
