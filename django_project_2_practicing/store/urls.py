from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()  # DefaultRouter   with this class we can access our endpoint in this url http://127.0.0.1:8000/hi/
# ,we can get the data in json  in this way -> http://127.0.0.1:8000/hi/products.json
router.register('products', ProductViewSet)
router.register('collections', CollectionViewSet)
router.register('carts', CartViewSet)
router.register('customers', CustomerViewSet)
router.register('orders', OrderViewSet, basename='order')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')  # it means we have product_pk in our router
products_router.register('reviews', ReviewViewSet, basename='product-reviews') # the name will be product-reviews-list or product-reviews-detail

cart_items = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items.register('items', CartItemViewSet, basename='cart-item')

urlpatterns = router.urls + products_router.urls + cart_items.urls

# urlpatterns = [
#     path('1/', function, name='function'),
#     path('products/', ProductList.as_view()),
#     path('products/<int:pk>', ProductDetail.as_view()),
#     path('collections/', CollectionList.as_view()),
#     path('collections/<int:pk>', CollectionDetail.as_view(), name='collection-handle')
# ]