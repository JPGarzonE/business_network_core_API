# Serializers profiles

# Django rest framework
from rest_framework import serializers

# Django
from django.contrib.auth.models import AnonymousUser

# models
from ..models import (
    Certificate, 
    SupplierProfile, 
    SupplierCertificate, 
    SupplierLocation, 
    SupplierSaleLocation,
    Product
)
from companies.models import UnregisteredRelationship, CompanyMember

# Serializers
from ..serializers import (
    CertificateModelSerializer,
    SupplierCertificateModelSerializer,
    SupplierLocationNestedModelSerializer,
    SupplierSaleLocationModelSerializer,
    ProductOverviewModelSerializer
)
from multimedia.serializers.images import ImageModelSerializer
from companies.serializers import UnregisteredRelationshipModelSerializer


class ProfileSupplierModelSerializer(serializers.ModelSerializer):
    """Supplier model serializer for the profile serializer."""

    accountname = serializers.CharField(source = "company.accountname")
    is_verified = serializers.BooleanField(source = "company.is_verified")
    logo = ImageModelSerializer(source = "company.logo")

    class Meta:

        model = SupplierProfile

        fields = (
            'accountname', 
            'is_verified', 
            'display_name', 
            'industry', 
            'description', 
            'contact_area_code',
            'contact_phone',
            'contact_email',
            'logo',
        )


class DocumentationSupplierProfileSerializer(serializers.Serializer):
    """This serializer is created uniquely for display 
    correctly the field data types for the API documentation"""

    editable = serializers.BooleanField()

    display_tutorial = serializers.BooleanField()

    company = ProfileSupplierModelSerializer()

    principal_location = SupplierLocationNestedModelSerializer()

    sale_locations = SupplierSaleLocationModelSerializer()

    products = ProductOverviewModelSerializer(many = True)

    certificates = SupplierCertificateModelSerializer(many = True)

    unregistered_relationships = UnregisteredRelationshipModelSerializer(many = True)


class SupplierProfileSerializer(serializers.Serializer):
    """Serializer for the data in a supplier profile."""

    requires_context = True

    editable = serializers.SerializerMethodField()

    display_tutorial = serializers.SerializerMethodField()

    supplier = ProfileSupplierModelSerializer()

    principal_location = serializers.SerializerMethodField()

    sale_locations = serializers.SerializerMethodField()

    products = serializers.SerializerMethodField()

    certificates = serializers.SerializerMethodField()

    unregistered_relationships = serializers.SerializerMethodField()


    def get_editable(self, instance):
        request = self.context['request']

        if type(request.user) is AnonymousUser:
            return False

        supplier = instance.get("supplier")

        try:
            company_member = CompanyMember.objects.get(
                company = supplier.company,
                user = request.user
            )

            company_member.number_of_logins_in_supplier_profile += 1
            company_member.save()
            self.context['user_number_of_logins'] = company_member.number_of_logins_in_supplier_profile
            self.context['editable'] = True

            return True
        except CompanyMember.DoesNotExist:
            self.context['editable'] = False
            return False

    def get_display_tutorial(self, instance):
        request = self.context['request']

        if type(request.user) is AnonymousUser or self.context['editable'] is False:
            return False

        logins_number = self.context['user_number_of_logins']

        if logins_number > 1:
            return False
        else:
            return True

    def get_principal_location(self, instance):
        supplier = instance.get("supplier")

        if supplier.principal_location:
            return SupplierLocationNestedModelSerializer(
                supplier.principal_location
            ).data
        else:
            return None

    def get_sale_locations(self, instance):
        supplier = instance.get("supplier")

        supplier_sale_locations = SupplierSaleLocation.objects.filter(
            supplier = supplier
        )
        return SupplierSaleLocationModelSerializer(supplier_sale_locations, many = True).data

    def get_products(self, instance):
        supplier = instance.get("supplier")

        supplier_products = Product.objects.filter(
            supplier = supplier
        )[:6]
        return ProductOverviewModelSerializer(supplier_products, many = True).data

    def get_certificates(self, instance):
        supplier = instance.get("supplier")

        supplier_certificates = SupplierCertificate.objects.filter(
            supplier = supplier
        )
        return SupplierCertificateModelSerializer(supplier_certificates, many = True).data

    def get_unregistered_relationships(self, instance):
        supplier = instance.get("supplier")
        company = supplier.company

        company_unregistered_relationships = UnregisteredRelationship.objects.filter(
            requester = company
        )
        return UnregisteredRelationshipModelSerializer(company_unregistered_relationships,
            many = True).data