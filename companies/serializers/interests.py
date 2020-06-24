"""Interest serializer."""

# Django rest framework
from rest_framework import serializers

# Models
from companies.models import Interest

class InterestModelSerializer(serializers.ModelSerializer):
    """Interest model serializer."""

    class Meta:
        """Interest meta class."""

        model = Interest

        fields = (
            'id',
            'company',
            'type',
            'name',
            'description',
            'priority'
        )

        read_only_fields = (
            'company'
            'media',
        )



class CreateCompanyInterestSerializer(serializers.Serializer):
    """Create company Interest"""

    requires_context = True

    name = serializers.CharField(
        min_length = 2,
        max_length = 50
    )

    type = serializers.CharField(
        min_length = 3,
        max_length = 60,
        required = False
    )

    description = serializers.CharField(
        min_length = 2,
        max_length = 155,
        required = False
    )

    priority = serializers.IntegerField(
        required = False
    )

    def create(self, data):
        """Create new company Dnaelement."""
        company = self.context['company']
        
        interest = Interest.objects.create(
            company = company,
            **data
        )

        return interest