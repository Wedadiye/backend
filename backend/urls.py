from django.urls import path ,include
from rest_framework import routers
from .views import CartItemViewSet, CategoryViewSet, OrderViewSet ,ProductViewSet

router=routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('produits', ProductViewSet ,basename='produit')
router.register('cart', CartItemViewSet, basename='cart-item')
router.register('commande', OrderViewSet, basename='commande')

urlpatterns = [
    path('', include(router.urls)),
    path('products/category/<int:category_id>', ProductViewSet.as_view({'get': 'list_products_by_category'}), name='product-list-by-category'),

]