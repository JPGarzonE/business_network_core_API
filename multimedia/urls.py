# multimedia/urls.py

from django.urls import include, path
from rest_framework import routers
from multimedia.views import *

router = routers.DefaultRouter()
router.register('files', FileViewSet)
router.register('images', ImageViewSet)

urlpatterns = [
    # path('files/', FileUploadAPIView.as_view(), name = 'files_upload'),

    path('', include(router.urls)),
]
