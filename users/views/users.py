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
from ..models import User
from companies.models import CompanyMember

# Serializer
from ..seralizers import UserIdentitySerializer, UserModelSerializer


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
        if self.action in ['list', 'retrieve']:
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


class UserIdentityAPIView(APIView):
    """User identity API view that identify and return a 
    user according the access token in the request headers 
    and all the companies where the user have access."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema( operation_id = "Me", tags = ["Me"], security = [{ "api-key": []}],
        operation_description = """
            Special endpoint that takes the access token of the request, 
            identify the user of that access token and return the respective 
            user with all the companies where the user have access.""",
        responses = { 200: UserIdentitySerializer, 404: openapi.Response("Not Found")}
    )
    def get(self, request, format = None, **kwargs):
        """Handle HTTP get for retrieving a user according its access token"""
        user_memberships = request.user.get_memberships()

        access_company, other_companies = self.filter_user_memberships(request, user_memberships)

        user_identity = {
            'user': request.user,
            'access_company': access_company,
            'other_companies': other_companies
        }

        identity_serializer = UserIdentitySerializer( user_identity )

        return Response( identity_serializer.data, status.HTTP_200_OK)

    def filter_user_memberships(self, request, user_memberships):
        """Recieves the request, takes the company accountname inside the auth token
        and filter the user_memberships list. Where divides the results in access company:
        the company of the auth token and the other companies where the user is member.
        """

        request_company_accountname = request.auth.payload.get('company_accountname')
        access_company = None
        other_companies = []

        for membership in user_memberships:
            if membership.company_accountname == request_company_accountname:
                access_company = membership.company
            else:
                other_companies.append(membership)

        return access_company, other_companies
