# market/urls.py

from django.urls import include, path
from market.views.showcases import ShowcaseFeedView

urlpatterns = [
    path('showcase/', ShowcaseFeedView.as_view()),
]