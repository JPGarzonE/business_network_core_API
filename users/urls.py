# users/urls.py

from django.urls import include, path
from rest_framework import routers
from users.views import UserViewSet, RelationshipViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register(
    'users/(?P<user_pk>[\w.]+)/relationships',
    RelationshipViewSet,
    basename = 'relationship'
)

urlpatterns = [
    path('', include(router.urls)),

    path(
        'api-auth/', 
        include('rest_framework.urls', namespace = 'rest_framework'),
    )
]