# Views dnaelements

# Constants
from companies.constants import VisibilityState

# Django
from django.utils.decorators import method_decorator

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Documentation
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Models
from ..models import SupplierProfile, DNAElement

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..permissions import IsSupplierMemberWithEditPermission

# Serializers
from ..serializers import DnaelementModelSerializer, HandleSupplierDnaelementSerializer


@method_decorator(name='list', decorator = swagger_auto_schema( operation_id = "List supplier DNA elements", tags = ["Supplier DNA"],
    operation_description = "Endpoint to list all the DNA elements of a supplier",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name='destroy', decorator = swagger_auto_schema( operation_id = "Delete a supplier DNA element", tags = ["Supplier DNA"],
    operation_description = "Endpoint to delete a DNA element of a supplier by username and id",
    responses = { 404: openapi.Response("Not Found") }, security = []
))
@method_decorator(name='update', decorator = swagger_auto_schema(auto_schema = None))
class DnaelementViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Dnaelement view set"""

    serializer_class = DnaelementModelSerializer
    supplier = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        accountname = kwargs['accountname']
        self.supplier = get_object_or_404(SupplierProfile, company__accountname = accountname)

        return super(DnaelementViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated, IsSupplierMemberWithEditPermission]

        return [permission() for permission in permissions]


    def get_data_owner_company(self):
        """Return the company owner of the data (The company of the supplier)"""
        return self.supplier.company


    def get_queryset(self):
        """Return supplier Dnaelements"""
        return DNAElement.objects.filter(
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the Dnaelement by the id"""
        dnaelement = get_object_or_404(
            DNAElement,
            id = self.kwargs['pk'],
            supplier = self.supplier,
            visibility = VisibilityState.OPEN.value
        )

        return dnaelement

    def perform_destroy(self, instance):
        """Disable Dnaelement."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()


    @swagger_auto_schema( tags = ["Supplier DNA"], request_body = HandleSupplierDnaelementSerializer,
        responses = { 200: DnaelementModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"name": ["this field is required"]} 
            })
        }, security = [{ "api-key": [] }])
    def create(self, request, *args, **kwargs):
        """Create supplier DNA element\n
            Endpoint to create a DNA element to a supplier with the accountname of the company owner given
        """
        try:
            dnaelement_serializer = HandleSupplierDnaelementSerializer(
                data = request.data,
                context = {'supplier': self.supplier}
            )
            dnaelement_serializer.is_valid(raise_exception = True)
            dnaelement = dnaelement_serializer.save()

            data = self.get_serializer(dnaelement).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)


    @swagger_auto_schema( tags = ["Supplier DNA"], request_body = HandleSupplierDnaelementSerializer,
        responses = { 200: DnaelementModelSerializer, 404: openapi.Response("Not Found"),
            401: openapi.Response("Unauthorized", examples = {"application/json": {"detail": "Invalid token."} }),
            400: openapi.Response("Bad request", examples = {"application/json":
                {"detail": "Theres no image with the id provided in 'image_id'"} 
            })
        }, security = [{ "api-key": [] }])
    def partial_update(self, request, *args, **kwargs):
        """Partial update a supplier DNA element\n
            Endpoint to partial update a DNA element of a supplier with the accountname of the company owner given
        """

        try:
            instance = self.get_object()
            dna_serializer = HandleSupplierDnaelementSerializer(
                instance = instance,
                data = request.data,
                partial = True
            )

            dna_serializer.is_valid(raise_exception = True)
            dna = dna_serializer.save()

            data = self.get_serializer(dna).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)


class DnaelementDetailView(APIView):
    """
        Retrieve the detail of a DNAElement.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema( tags = ["Supplier DNA"],
        responses = { 200: DnaelementModelSerializer, 404: openapi.Response("Not Found")}, security = []
    )
    def get(self, request, pk, format = None):
        """Retrieve a supplier DNA element.\n
            Endpoint to retrieve a DNA element by its id.
        """
        dnaelement = self.get_object(pk)
        serializer = DnaelementModelSerializer(dnaelement)

        return Response(serializer.data)

    def get_object(self, pk):
        dnaelement = get_object_or_404(
            DNAElement,
            id = pk,
            visibility = VisibilityState.OPEN.value
        )

        return dnaelement