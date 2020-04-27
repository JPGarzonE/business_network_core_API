"""Products serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Product

class ProductModelSerializer(serializers.ModelSerializer):
    """Product model serializer."""

    class Meta:
        """Product meta class."""

        model = Product

        fields = (
            'id',
            'company',
            'category',
            'name',
            'price',
            'description',
            'media'
        )

        read_only_fields = (
            'company'
            'media',
        )



class CreateCompanyProductSerializer(serializers.Serializer):
    """Create company service"""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 50
    )

    category = serializers.CharField(
        min_length = 3,
        max_length = 60
    )

    description = serializers.CharField(
        min_length = 2,
        max_length = 155,
        required = False
    )

    price = serializers.CharField(
        min_length = 2,
        max_length = 20,
        required = False
    )

    def create(self, data):
        """Create new company product."""
        company = self.context['company']
        
        product = Product.objects.create(
            company = company,
            **data
        )

        return product