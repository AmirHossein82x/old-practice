from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from store.models import Collection, Product, Review, Cart, CartItems, Customer, Order, OrderItem
from store.signals import order_create


class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    # collection = serializers.StringRelatedField()
    # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    # collection = CollectionSerializer()
    collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(), view_name='collection-handle')

class ProductSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'price_with_tax', 'collection']

    # collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(), view_name='collection-handle')
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
    price_with_tax = serializers.SerializerMethodField(method_name='new_price')

    def new_price(self, product):
        return product.unit_price // Decimal(2)

class CollectionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    """this way ends up with lots of query"""
    # products = serializers.SerializerMethodField(method_name='product_count')
    #
    # def product_count(self, collection):
    #     return collection.product_set.count()

    products_count = serializers.IntegerField(read_only=True)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'data', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
class ProductSerializer3(serializers.ModelSerializer):
    collection = serializers.SerializerMethodField()

    def get_collection(self, product):
        return product.collection.title

    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'collection']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer3()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItems
        fields = ['product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    cart_price = serializers.SerializerMethodField()

    def get_cart_price(self, cart):
        return sum([item.product.unit_price * item.quantity for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'cart_price']
        # baa2b478-502a-4cc6-a62c-def1441bb21b

class CartItemSerializer2(serializers.ModelSerializer):
    product = ProductSerializer3()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItems
        fields = ['id', 'product', 'quantity', 'total_price']

class AddProductSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('this product does not exist')
        return value

    class Meta:
        model = CartItems
        fields = ['product_id', 'quantity']

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        cart_id = self.context['cart_id']
        quantity = self.validated_data['quantity']
        if not CartItems.objects.filter(product_id=product_id, cart_id=cart_id).exists():
            cart_item = CartItems.objects.create(cart_id=cart_id, **self.validated_data)
            self.instance = cart_item
        else:
            cart_item = CartItems.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItems
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Customer
        fields = ['user', 'phone', 'birth_date', 'membership']

    def save(self, **kwargs):
        print(kwargs)
        if Customer.objects.filter(user_id=self.context.get('user_id')).exists():
            raise serializers.ValidationError({'this user already has a profile'})
        else:
            customer = Customer.objects.create(user_id=self.context['user_id'], **self.validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title',  'unit_price']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'customer', 'items']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            return serializers.ValidationError('this cart does not exist')
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data.get('cart_id')
            customer, created = Customer.objects.get_or_create(user_id=self.context['user_id'])

            order = Order.objects.create(customer=customer)
            cart_items = CartItems.objects.select_related('product').filter(cart_id=cart_id)
            order_item = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_item)
            Cart.objects.filter(id=cart_id).delete()
            order_create.send_robust(self.__class__, order=order)


