# serializers.py

# Django REST Framework
from rest_framework import serializers

# Models
from ..models import CompanyMember


class CompanyMember_UserPerspective(serializers.ModelSerializer):

    accountname = serializers.CharField(source = 'company_accountname')
    name = serializers.CharField(source = 'company_name')

    class Meta:
        model = CompanyMember

        fields = (
            'accountname',
            'name'
        )


class CompanyMember_CompanyPerspective(serializers.ModelSerializer):

    username = serializers.CharField(source = 'user_username')
    full_name = serializers.CharField(source = 'user_full_name')
    email = serializers.CharField(source = 'user_email')

    class Meta:
        model = CompanyMember

        fields = (
            'username',
            'fullname',
            'email'
        )