# URLs suppliers

from django.urls import include, path
from rest_framework import routers
from .views import (
    SupplierViewSet, SupplierSummaryViewSet,
    SupplierLocationViewSet, SupplierSaleLocationViewSet,
    ProductViewSet, DnaelementViewSet,
    SupplierCertificateViewSet, CurrencyViewSet, CertificateDetailView,
    SupplierProfileView,
    DnaelementDetailView, ProductDetailView, DeleteProductCertificateView,
    DeleteProductImageView,
)


router = routers.DefaultRouter()

router.register(
    'suppliers', 
    SupplierViewSet,
    basename = 'suppliers'
)
router.register(
    'suppliers/(?P<accountname>[\w.]+)/locations',
    SupplierLocationViewSet,
    basename = 'Operative location'
)
router.register(
    'suppliers/(?P<accountname>[\w.]+)/sale-locations',
    SupplierSaleLocationViewSet,
    basename = 'Sale location'
)
router.register(
    'suppliers/(?P<accountname>[\w.]+)/products',
    ProductViewSet,
    basename = 'product'
)
router.register(
    'suppliers/(?P<accountname>[\w.]+)/dnaelements',
    DnaelementViewSet,
    basename = 'dnaelement'
)
router.register(
    'suppliers/(?P<accountname>[\w.]+)/certificates',
    SupplierCertificateViewSet,
    basename = 'certificates'
)

router.register(
    'currencies',
    CurrencyViewSet,
    basename = 'currencies'
)

urlpatterns = [
    path('', include(router.urls)),

    path('certificates/<int:pk>/', CertificateDetailView.as_view()),

    path('suppliers/<accountname>/profile/', SupplierProfileView.as_view()),

    path('suppliers/<accountname>/summary/', SupplierSummaryViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})),

    path('dnaelements/<int:pk>/', DnaelementDetailView.as_view()),

    path('products/<int:pk>/', ProductDetailView.as_view()),

    path('products/<int:product_id>/certificates/<int:certificate_id>/', DeleteProductCertificateView.as_view()),

    path('products/<int:product_id>/images/<int:image_id>/', DeleteProductImageView.as_view()),

]