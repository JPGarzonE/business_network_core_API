# Views authentication

# Documentation
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Rest framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
 
# SimpleJWT
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


# Serializers
from ..seralizers import (
    AuthenticationTokensResponseSerializer,
    LoginAccessSerializer,
    UserAuthenticationTokenSerializer,
    UserAuthenticationTokenRefreshSerializer
)


class LoginView(TokenObtainPairView):
    """
    View made to implement JWT Login in the platform.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserAuthenticationTokenSerializer

    @swagger_auto_schema( tags = ["Authentication"], request_body = UserAuthenticationTokenSerializer,
        responses = { 201: LoginAccessSerializer,
            400: openapi.Response("Bad request", examples = {"application/json": [
                {"detail": "No active account found with the given credentials" }
            ]} )
        }, security = []
    )
    def post(self, request, *args, **kwargs):
        """
        Login\n
        Endpoint for login a user in the system. \n
        Return an `access` token (that expires each 15 min) for grant future access and
        a `refresh` token (that expires each day) to renew both tokens in the `Refresh token` endpoint.\n
        Each token generated by the system gives user access to only one specific company where is member.
        If the user want to make actions over other different company where is member, it have to
        change the company in the refresh endpoint.
        """

        tokens_serializer = self.get_serializer(data=request.data)
        
        try:
            tokens_serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        user = tokens_serializer.validated_data.pop('user')
        tokens_data = tokens_serializer.validated_data

        user_memberships = user.get_memberships()

        login_response_data = {
            'tokens': tokens_data,
            'user': user,
            'access_company': user_memberships[0].company if user_memberships else None,
            'other_companies': user_memberships[1:]
        }

        login_serializer = LoginAccessSerializer( login_response_data )

        return Response(login_serializer.data, status=status.HTTP_200_OK)


@method_decorator( name = 'post', decorator = swagger_auto_schema( 
    operation_id = "Refresh token", tags = ["Authentication"],
    operation_description = """
        Endpoint to renew the authentication tokens.\n
        It returns a renewed access token (expires each 15 min) and a renewed refresh token 
        (expires each day). Also is possible to change the token company for access to another accounts.""",
    manual_parameters = [
        openapi.Parameter(name = "company", in_ = openapi.IN_QUERY, type = "String",
            description = "Recieves the accountname of the company where it wants to change the access.")
    ],
    request_body = UserAuthenticationTokenRefreshSerializer,
    responses = { 201: AuthenticationTokensResponseSerializer,
        401: openapi.Response("Bad request", examples = {"application/json": [
            {"detail": "Token is invalid or expired", "code": "token_not_valid" }
        ]} )
    }, security = []
))
class UserTokenRefreshView(TokenRefreshView):
    """
    View made to change the access company when refreshing a user token.
    """

    serializer_class = UserAuthenticationTokenRefreshSerializer

    def get_serializer_context(self):
        """
        Add extra information to the serializer context 
        to pass important data to serializer methods.
        """
        company_accountname = self.request.query_params.get('company')

        context = super().get_serializer_context()
        context.update(
            {'company_accountname': company_accountname}
        )
        return context