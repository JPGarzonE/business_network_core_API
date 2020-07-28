# users/urls.py

from django.urls import include, path
from rest_framework import routers
from users.views import (
    AccountVerificationAPIView, 
    RelationshipViewSet,
    SentRelationshipRequestViewSet,
    RecievedRelationshipRequestViewSet,
    RelationshipRequestViewSet,
    UserViewSet, 
    UserVerificationAPIView,
    UserVerificationTokenAPIView
)

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register(
    'users/(?P<user_pk>[\w.]+)/relationships',
    RelationshipViewSet,
    basename = 'relationship'
)
router.register(
    'me/relationship-requests/sent',
    SentRelationshipRequestViewSet,
    basename = 'sent_relationship_request'
)
router.register(
    'me/relationship-requests/recieved',
    RecievedRelationshipRequestViewSet,
    basename = 'recieved_relationship_request'
)
router.register(
    'users/(?P<target_user_id>[\w.]+)/relationship-requests',
    RelationshipRequestViewSet,
    basename = 'external_relationship_request'
)

urlpatterns = [
    path('users/verify/', AccountVerificationAPIView.as_view(), name = 'verify_account'),
    path('users/<username>/verification/token/', UserVerificationTokenAPIView.as_view(), name="user_verification"),
    path('me/verification/', UserVerificationAPIView.as_view(), name = 'user_verification_me'),

    path('', include(router.urls)),

    path(
        'api-auth/', 
        include('rest_framework.urls', namespace = 'rest_framework'),
    ),

]