# companies/urls.py

from django.urls import include, path
from rest_framework import routers
from companies.views import *


router = routers.DefaultRouter()
router.register('companies', CompanyViewSet)
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

urlpatterns = [
    path('', include(router.urls)),

    path('products/<int:pk>/', ProductDetailView.as_view()),

    path('services/<int:pk>/', ServiceDetailView.as_view()),

    path('dnaelements/<int:pk>/', DnaelementDetailView.as_view()),
]