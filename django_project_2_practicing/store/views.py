from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Value, F, Func, ExpressionWrapper, DecimalField, PositiveIntegerField
from django.db.models.aggregates import Count, Max
from django.db.models.functions import Concat, ExtractDay, Chr, Left, LPad
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework import mixins
from rest_framework import permissions
from .permissoin import IsAdminOrReadOnly


from .models import Product, OrderItem, Order, Customer, Collection, Promotion, Cart, Review, CartItems
from tags.models import TagItem
from django.contrib.contenttypes.models import ContentType

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

# Create your views here.
from .serializer import ProductSerializer2, CollectionSerializer, CollectionSerializer2, ReviewSerializer, \
    CartSerializer, CartItemSerializer2, AddProductSerializer, UpdateCartItemSerializer, CustomerSerializer, \
    OrderSerializer, CreateOrderSerializer

from .filters import ProductFilter, CustomSearchFilter
from .pagination import CustomPagination


def function(request):
    query_set1 = Product.objects.filter(collection_id__gt=3).order_by('-collection_id').values('collection_id', 'title')
    query_set = Product.objects.filter(Q(collection_id=3) | Q(unit_price__gt=100))
    query_set = Product.objects.filter(orderitem__unit_price__gt=80).values('orderitem__quantity')
    query_set = Order.objects.filter(payment_status='P')
    query_set = Customer.objects.filter(~Q(id__in=Order.objects.values('customer_id')))
    query_set1 = OrderItem.objects.select_related('order__customer').all()
    # query_set = Order.objects.select_related('orderitem_set').all()
    query_set1 = Product.objects.prefetch_related('promotion').all()
    query_set = Customer.objects.prefetch_related('order_set')
    query_set = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    query_set = OrderItem.objects.prefetch_related('product').all()
    query_set = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct())
    query_set = Product.objects.aggregate(number_of_products=Count('id'), max_price=Max('unit_price'))
    query_set = Product.objects.annotate(new_id=Value(True))
    discount = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    query_set = Product.objects.annotate(new_price=discount)
    func = Customer.objects.annotate(full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT'))
    func = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
    func = Product.objects.annotate(date_day=ExtractDay('last_update'))
    func = Customer.objects.annotate(new_row=Left('last_name', 2))
    func = Customer.objects.annotate(new=LPad('first_name', length=2))
    content_type = ContentType.objects.get_for_model(Product)
    query_set = TagItem.objects.filter(content_type=content_type, object_id=1)

    query_set = TagItem.objects.get_for_content(Product, 1)
    query_set = TagItem.objects.all()
    query_set = TagItem.new_object.all()
    # query_set = TagItem.objects.all_new_product()   Attribute Error
    query_set = TagItem.new_object.all_new_product()

    # new_tag_item = TagItem.objects.create()  wqy 1
    """way 2"""
    # new_tag = TagItem()
    # new_tag.content_type = 2
    # new_tag.save()
    query_set = Order.objects.values('customer_id').annotate(count=Count('customer_id'))  # group by customer_id
    query_set = Customer.objects.values('membership').annotate(Count('id'))
    query_set = Product.objects.values('collection').annotate(Count('id'))
    query_set = Order.objects.values('customer_id').annotate(Count('id'))
    query_set = Order.objects.select_related('customer__address')
    query_set = Customer.objects.filter(pk__in=Order.objects.values('customer_id'))
    query_set10 = Order.objects.prefetch_related('customer')
    query_set1 = Customer.objects.prefetch_related('order_set')
    query_set = Product.objects.prefetch_related('collection')

    query_set = Product.objects.prefetch_related('collection')
    query_set = Collection.objects.filter(id__in=Product.objects.values('collection'))
    query_set = Collection.objects.exclude(id__in=Product.objects.values('collection'))
    # query_set = Product.objects.filter(products_order__quantity=2)
    # query_set = Product.objects.select_related('orderitem_set').filter(quantity__gt=2).values('inventory')

    return render(request, 'sample.html', context={'query_set': query_set})

@api_view(['GET', 'POST'])
def handler(request):
    if request.method == 'GET':
        query_set = Product.objects.select_related('collection').all()
        serializer = ProductSerializer2(query_set, many=True,  context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer2(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', "PUT", 'DELETE'])
def detail_handler(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'GET':
        serializer = ProductSerializer2(product, context={'request': request})
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProductSerializer2(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if product.orderitem_set.count() > 0:
            return Response({'error': 'you can not delete this product because it has been ordered'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', "PUT", "DELETE"])
def collection_handle(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer2(collection)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CollectionSerializer2(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.product_set.count() > 0:
            return Response({'error': 'this collection can not be deleted'})
        else:
            collection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        query_set = Collection.objects.annotate(products_count=Count('products'))
        serializer = CollectionSerializer2(query_set, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializer2(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductViewSet(ModelViewSet):  # we can use ReadOnlyModelViewSet and in this case we can not delete and update the product
    queryset = Product.objects.all()
    serializer_class = ProductSerializer2
    filter_backends = [DjangoFilterBackend, CustomSearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['^title']
    ordering_fields = ['unit_price', 'last_update']
    pagination_class = CustomPagination
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).exists():
            return Response({"Error": "this product can not be deleted"})
        return super(ProductViewSet, self).destroy(request, *args, **kwargs)

    # def delete(self, request, pk):
    #     product = get_object_or_404(Product, pk=pk)
    #     if product.orderitem_set.count() > 0:
    #         return Response({"Error": "this product can not be deleted"})
    #     else:
    #         product.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

# class ProductList(ListCreateAPIView, ProductViewSet):
#     # queryset = Product.objects.all()
#     # serializer_class = ProductSerializer2
#
# class ProductDetail(RetrieveUpdateDestroyAPIView, ProductViewSet):
#     # queryset = Product.objects.all()
#     # serializer_class = ProductSerializer2

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer2

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).exists():
            return Response({"Error": 'you can not delete this collection'})
        return super(CollectionViewSet, self).destroy(request, *args, **kwargs)

    # def delete(self, request, pk):     if we use delete function the delete button will appear in the list view
    #     collection = get_object_or_404(Collection, pk=pk)
    #     if collection.products.count() > 0:
    #         return Response({"Error": 'you can not delete this collection'})
    #     else:
    #         collection.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

# class CollectionList(ListCreateAPIView):
#
# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products'))
#     serializer_class = CollectionSerializer2


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product')
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return CartItems.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product__collection')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddProductSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        else:
            return CartItemSerializer2

    def get_serializer_context(self):
        context = super(CartItemViewSet, self).get_serializer_context()
        context['cart_id'] = self.kwargs['cart_pk']
        return context

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        customer, created = Customer.objects.get_or_create(user_id=request.user.id)
        if self.request.method == 'GET':
            customer_serializer = CustomerSerializer(customer)
            return Response(customer_serializer.data)
        elif self.request.method == 'PUT':
            customer_serializer = CustomerSerializer(customer, data=customer)
            customer_serializer.is_valid(raise_exception=True)
            customer_serializer.save()
            return Response(customer_serializer.data)
        # else:
        #     customer_serializer = CustomerSerializer(customer)
        #     return Response(customer_serializer.data)

    def get_serializer_context(self):
        context = super(CustomerViewSet, self).get_serializer_context()
        context.update({'user_id': self.request.user.id})
        return context

class OrderViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        user_id = self.request.user.id
        customer_id, created = Customer.objects.only('id').get_or_create(user_id=user_id)
        return Order.objects.filter(customer_id=customer_id)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        context = super(OrderViewSet, self).get_serializer_context()
        context['user_id'] = self.request.user.id
        return context


