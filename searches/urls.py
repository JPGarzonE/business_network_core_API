# Searches/urls.py

from django.urls import include, path
from rest_framework import routers

# other local apps
from searches.views import *

router = routers.DefaultRouter()
router.register('companies', SearchCompaniesView)

urlpatterns = [
    path('', include(router.urls)),
]
