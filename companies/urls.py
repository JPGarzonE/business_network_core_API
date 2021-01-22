# users/urls.py

from django.urls import include, path
from rest_framework import routers
from .views import (
    VerifyCompanyAPIView, 
    RelationshipViewSet,
    SentRelationshipRequestViewSet,
    RecievedRelationshipRequestViewSet,
    RelationshipRequestViewSet,
    CompanyVerificationAPIView,
    CompanyVerificationTokenAPIView,
    CompanyViewSet,
    UnregisteredCompanyViewSet,
    UnregisteredRelationshipViewSet
)

router = routers.DefaultRouter()
router.register(
    'companies', 
    CompanyViewSet,
    basename = 'companies'
)
router.register(
    'unregistered-companies',
    UnregisteredCompanyViewSet,
    basename = 'unregistered_companies'
)
router.register(
    'companies/(?P<requester_company_accountname>[\w.]+)/unregistered-relationships',
    UnregisteredRelationshipViewSet,
    basename = 'unregistered_relationships'
)
router.register(
    'companies/(?P<accountname>[\w.]+)/relationships',
    RelationshipViewSet,
    basename = 'relationship'
)
router.register(
    'companies/(?P<accountname>[\w.]+)/relationship-requests/sent',
    SentRelationshipRequestViewSet,
    basename = 'sent_relationship_request'
)
router.register(
    'companies/(?P<accountname>[\w.]+)/relationship-requests/recieved',
    RecievedRelationshipRequestViewSet,
    basename = 'recieved_relationship_request'
)
router.register(
    'companies/(?P<target_company_accountname>[\w.]+)/relationship-requests/(?P<requester_company_accountname>[\w.]+)',
    RelationshipRequestViewSet,
    basename = 'external_relationship_request'
)

urlpatterns = [
    path('companies/<accountname>/verification/', CompanyVerificationAPIView.as_view(), name = 'company_verification'),

    path('companies/verification/verify/', VerifyCompanyAPIView.as_view(), name = 'verify_company'),
    path('companies/<accountname>/verification/token/', CompanyVerificationTokenAPIView.as_view(), name="company_verification_token"),

    path('', include(router.urls)),
]