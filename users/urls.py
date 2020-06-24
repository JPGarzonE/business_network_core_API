# users/urls.py

from django.urls import include, path
from rest_framework import routers
from users.views import AccountVerificationAPIView, UserViewSet, RelationshipViewSet, UserVerificationAPIView
# from users.views.user import 

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register(
    'users/(?P<user_pk>[\w.]+)/relationships',
    RelationshipViewSet,
    basename = 'relationship'
)

urlpatterns = [
    path('users/verify/', AccountVerificationAPIView.as_view(), name = 'verify_account'),
    path('me/verification/', UserVerificationAPIView.as_view(), name = 'user_verification'),

    path('', include(router.urls)),

    path(
        'api-auth/', 
        include('rest_framework.urls', namespace = 'rest_framework'),
    ),

]