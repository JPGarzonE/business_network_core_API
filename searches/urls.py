# Searches/urls.py

from django.urls import include, path
from rest_framework import routers

# other local apps
from searches.views import *

router = routers.DefaultRouter()
router.register('companies', SearchCompaniesViewSet, basename="search__companies")
router.register('companies/unregistered', SearchUnregisteredCompaniesViewSet, basename="search__unregistered_companies")
router.register('products', SearchShowcaseProductsViewSet, basename="search__products")

urlpatterns = [
    path('', include(router.urls)),
]
