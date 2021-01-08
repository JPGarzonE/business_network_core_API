# URLs buyers

from django.urls import include, path
from rest_framework import routers

from .views import (
    BuyerProfileView,
    BuyerViewSet
)

router = routers.DefaultRouter()

router.register(
    'buyers',
    BuyerViewSet,
    basename = 'buyers'
)

urlpatterns = [
    path('', include(router.urls)),

    path('buyers/<accountname>/profile/', BuyerProfileView.as_view())
]