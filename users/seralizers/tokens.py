# Serializers tokens

# Companies models
from companies.models import CompanyMember

# Django rest framework
from rest_framework import serializers

# SimpleJWT
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# User models
from ..models import User


class UserAuthenticationTokenSerializer(TokenObtainPairSerializer):
    """
    Serializer made for customize the user authentication token.\n
    This serializer authenticate the user in the validate method receiving
    its email and password. After that leaves the user object in self.user
    """

    @classmethod
    def get_token(cls, user):
        """Add data to the token payload."""

        token = super().get_token(user)

        default_membership = user.get_default_membership()

        if default_membership:
            # Is a user member of a company. If not, could be an
            # admin or another type of non company member user.
            token['company_accountname'] = default_membership.company_accountname

        token['username'] = user.username

        return token

    def validate(self, attrs):
        """Add the user to the validated data."""

        data = super().validate(attrs)
        data['user'] = self.user

        return data


class UserAuthenticationTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Serializer to refresh the authorization tokens.
    """

    def validate(self, attrs):
        company_accountname = self.context.get('company_accountname')
        
        if company_accountname:
            # The token has to change of access company
            refresh = RefreshToken(attrs['refresh']) # This initialization validates the token correcteness
            user = User.objects.get( username = refresh.payload['username'] )

            if not user.is_member(company_accountname):
                raise InvalidToken("The user is not a member of the company to which he wants to change access.")

            refresh.payload.update({
                'company_accountname': company_accountname
            })

            attrs['refresh'] = str(refresh)

        return super().validate(attrs)


class AuthenticationTokensResponseSerializer(serializers.Serializer):
    """
    Serializer made for represent the response of the 
    authentication tokens used in the platform.
    """

    access = serializers.CharField(
        help_text = """Token used for identify and grant access 
            to a user in the different endpoints of the platform. 
            (Expires each 15 min but can be refreshed)"""
    )

    refresh = serializers.CharField(
        help_text = """Token used for identify and grant access 
            to a user in the different endpoints of the platform. 
            (Expires each day but can be refreshed)"""
    )