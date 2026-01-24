from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CategoryViewSet, ProductViewSet, CardViewSet, OrderViewSet

router = DefaultRouter()
# 'basename' mánisi testtegi reverse('user-list') mánisine tásir etedi
router.register(r'users', UserViewSet, basename='user') 
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'card', CardViewSet, basename='card')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]