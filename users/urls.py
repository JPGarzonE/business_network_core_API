# Users urls

from django.urls import include, path
from rest_framework import routers

from .views import (
    UserViewSet, 
    UserIdentityAPIView, 
    LoginView, 
    UserTokenRefreshView
)

router = routers.DefaultRouter()

router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('login/', LoginView.as_view(), name = 'user_login'),
    path('me/', UserIdentityAPIView.as_view(), name = 'user_me'),
    path('token/refresh/', UserTokenRefreshView.as_view(), name = 'token_refresh'),
]
