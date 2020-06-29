# serializers/unregistered_companies.py

# Django-rest serializers
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

# Django
from django.db import transaction

# Models
from companies.models import UnregisteredCompany

class UnregisteredCompanyModelSerializer(serializers.ModelSerializer):

    name = serializers.CharField(
        max_length=60,
        validators=[UniqueValidator(queryset=UnregisteredCompany.objects.all())]
    )

    nit = serializers.CharField(
        max_length = 11,
        validators = [
            RegexValidator(
                regex = r'(\d{9,9}((.)\d)?)',
                message = "El nit debe estar acorde al formato de la registraduria"
            )
        ],

        required = False
    )

    industry = serializers.CharField(max_length=60)

    email = serializers.EmailField(
        validators = [ UniqueValidator( queryset = UnregisteredCompany.objects.all() ) ],
        required = False
    )

    country = serializers.CharField(
        min_length = 2,
        max_length = 40,
        required = False
    )

    city = serializers.CharField(
        min_length = 1,
        max_length = 40,
        required = False
    )

    class Meta():
        model = UnregisteredCompany
        fields = ('id', 'name', 'nit', 'industry', 'email', 'city', 'country')