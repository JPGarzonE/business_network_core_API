# serializers.py

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Models
from companies.models import Company
from django.contrib.auth import get_user_model
from users.models import Verification

class CompanyModelSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        min_length=4,
        max_length=60,
        validators=[UniqueValidator(queryset=Company.objects.all())]
    )

    nit = RegexValidator(
        regex = r'(\d{6,11}((.)\d)?)',
        message = "El nit debe estar acorde al formato de la registraduria"
    )

    description = serializers.CharField(
        max_length = 150,
        required = False,
        allow_null = True
    )

    web_url = serializers.CharField(
        max_length = 70,
        required = False,
        allow_null = True
    )

    class Meta:
        model = Company
        fields = ('id', 'name', 'nit', 'industry', 
            'web_url', 'description')