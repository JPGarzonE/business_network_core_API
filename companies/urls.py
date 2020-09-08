# companies/urls.py

from django.urls import include, path
from rest_framework import routers
from companies.views import *


router = routers.DefaultRouter()

router.register(
    'companies/unregistered',
    UnregisteredCompanyViewSet,
    basename = 'unregistered_companies'
)
router.register(
    'relationships/unregistered',
    UnregisteredRelationshipViewSet,
    basename = 'unregistered_relationships'
)
router.register(
    'companies', 
    CompanyViewSet,
    basename = 'companies'
)
router.register(
    'companies/(?P<username>[\w.]+)/locations',
    LocationViewSet,
    basename = 'location'
)
router.register(
    'companies/(?P<username>[\w.]+)/contacts',
    ContactViewSet,
    basename = 'contact'
)
router.register(
    'companies/(?P<username>[\w.]+)/products',
    ProductViewSet,
    basename = 'product'
)
router.register(
    'companies/(?P<username>[\w.]+)/services',
    ServiceViewSet,
    basename = 'service'
)
router.register(
    'companies/(?P<username>[\w.]+)/dnaelements',
    DnaelementViewSet,
    basename = 'dnaelement'
)
router.register(
    'companies/(?P<username>[\w.]+)/interests',
    InterestViewSet,
    basename = 'interest'
)

router.register(
    'companies/(?P<username>[\w.]+)/certificates',
    CompanyCertificateViewSet,
    basename = 'certificates'
)

urlpatterns = [
    path('', include(router.urls)),

    path('certificates/<int:pk>/', CertificateDetailView.as_view()),

    path('companies/<username>/relationships/unregistered/', ListUnregisteredRelationships.as_view()),

    path('dnaelements/<int:pk>/', DnaelementDetailView.as_view()),

    path('products/<int:pk>/', ProductDetailView.as_view()),

    path('products/<int:product_id>/certificates/<int:certificate_id>/', DeleteProductCertificateView.as_view()),

    path('products/<int:product_id>/images/<int:image_id>/', DeleteProductImageView.as_view()),

    path('services/<int:pk>/', ServiceDetailView.as_view()),

]