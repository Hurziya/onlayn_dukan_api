from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, CardViewSet, OrderViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'card', CardViewSet, basename='card')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]