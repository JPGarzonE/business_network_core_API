"""Company DNAElements views."""

# Django REST framework
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

# Models
from companies.models import Company, Dnaelement, VisibilityState

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from companies.permissions import IsCompanyAccountOwner, IsDataOwner

# Serializers
from companies.serializers import DnaelementModelSerializer, HandleCompanyDnaelementSerializer

class DnaelementViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """Dnaelement view set"""

    serializer_class = DnaelementModelSerializer
    company = None

    def dispatch(self, request, *args, **kwargs):
        """Verifiy that the company exists"""
        username = kwargs['username']
        self.company = get_object_or_404(Company, user__username = username)

        return super(DnaelementViewSet, self).dispatch(request, *args, **kwargs)

    def get_account_entity(self):
        """Return the entity father of the data."""
        return self.company

    def get_permissions(self):
        """Assign permission based on action"""
        if self.action in ['list']:
            permissions = [AllowAny]
        elif self.action in ['create']:
            permissions = [IsAuthenticated, IsCompanyAccountOwner]
        else:
            permissions = [IsAuthenticated, IsCompanyAccountOwner, IsDataOwner]

        return [permission() for permission in permissions]


    def get_queryset(self):
        """Return company Dnaelements"""
        return Dnaelement.objects.filter(
            company = self.company,
            visibility = VisibilityState.OPEN.value
        )

    def get_object(self):
        """Return the Dnaelement by the id"""
        dnaelement = get_object_or_404(
            Dnaelement,
            id = self.kwargs['pk'],
            visibility = VisibilityState.OPEN.value
        )

        return dnaelement

    def perform_destroy(self, instance):
        """Disable Dnaelement."""
        instance.visibility = VisibilityState.DELETED.value
        instance.save()

    def create(self, request, *args, **kwargs):
        """Handle Dnaelement creation."""
        try:
            dnaelement_serializer = HandleCompanyDnaelementSerializer(
                data = request.data,
                context = {'company': self.company}
            )
            dnaelement_serializer.is_valid(raise_exception = True)
            dnaelement = dnaelement_serializer.save()

            data = self.get_serializer(dnaelement).data
            data_status = status.HTTP_201_CREATED
        except Exception as e:
            data = {"detail": str(e)}
            data_status = status.HTTP_400_BAD_REQUEST
        
        return Response(data, status = data_status)

    def partial_update(self, request, *args, **kwargs):
        """Handle dna partial update and add a 
        image to a dna by its id if its the case"""
        try:
            instance = self.get_object()
            dna_serializer = HandleCompanyDnaelementSerializer(
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

    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format = None):
        """Return the dnaelement by the id"""
        dnaelement = self.get_object(pk)
        serializer = DnaelementModelSerializer(dnaelement)

        return Response(serializer.data)

    def get_object(self, pk):
        dnaelement = get_object_or_404(
            Dnaelement,
            id = pk,
            visibility = VisibilityState.OPEN.value
        )

        return dnaelement