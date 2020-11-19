"""Profiles serializer."""

# Django rest framework
from rest_framework import serializers

# models
from companies.models import (
    Certificate, Company, CompanyCertificate, CompanyLocation, CompanySaleLocation, 
    Contact, Product, UnregisteredRelationship, VisibilityState
)

# Serializers
from companies.serializers import (
    CertificateModelSerializer,
    CompanyCertificateModelSerializer,
    CompanyLocationNestedModelSerializer,
    ContactModelSerializer,
    CompanySaleLocationModelSerializer,
    ProductOverviewModelSerializer,
    UnregisteredRelationshipModelSerializer
)
from multimedia.serializers.images import ImageModelSerializer


class ProfileCompanyModelSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")
    is_verified = serializers.CharField(source="user.is_verified")
    logo = ImageModelSerializer()

    class Meta:

        model = Company

        fields = (
            'username', 'is_verified', 'name', 'industry', 
            'web_url', 'description', 'logo'
        )


class SupplierProfileSerializer(serializers.Serializer):
    """Serializer for the data in a supplier profile."""

    requires_context = True

    editable = serializers.SerializerMethodField()

    company = ProfileCompanyModelSerializer()

    principal_contact = serializers.SerializerMethodField()

    principal_location = serializers.SerializerMethodField()

    sale_locations = serializers.SerializerMethodField()

    products = serializers.SerializerMethodField()

    certificates = serializers.SerializerMethodField()

    unregistered_relationships = serializers.SerializerMethodField()


    def get_editable(self, instance):
        request = self.context['request']
        company = instance.get("company")

        return request.user.username == company.user.username

    def get_principal_contact(self, instance):
        company = instance.get("company")

        if company.principal_contact and company.principal_contact.visibility is VisibilityState.OPEN.value:
            return ContactModelSerializer(
                company.principal_contact
            ).data
        else:
            return None

    def get_principal_location(self, instance):
        company = instance.get("company")

        if company.principal_location and company.principal_location.visibility is VisibilityState.OPEN.value:
            return CompanyLocationNestedModelSerializer(
                company.principal_location
            ).data
        else:
            return None

    def get_sale_locations(self, instance):
        company = instance.get("company")

        company_sale_locations = CompanySaleLocation.objects.filter(
            company = company, visibility = VisibilityState.OPEN.value
        )
        return CompanySaleLocationModelSerializer(company_sale_locations, many = True).data

    def get_products(self, instance):
        company = instance.get("company")

        company_products = Product.objects.filter(
            company = company, visibility = VisibilityState.OPEN.value
        )
        return ProductOverviewModelSerializer(company_products, many = True).data

    def get_certificates(self, instance):
        company = instance.get("company")

        company_certificates = CompanyCertificate.objects.filter(
            company = company, visibility = VisibilityState.OPEN.value
        )
        return CompanyCertificateModelSerializer(company_certificates, many = True).data

    def get_unregistered_relationships(self, instance):
        company = instance.get("company")

        company_unregistered_relationships = UnregisteredRelationship.objects.filter(
            requester = company,
            visibility = VisibilityState.OPEN.value
        )
        return UnregisteredRelationshipModelSerializer(company_unregistered_relationships,
            many = True).data