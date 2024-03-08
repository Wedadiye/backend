"""
Serializer of shop api.
"""
from rest_framework import serializers

from backend.models import Category, Order, OrderItem, Product ,Cart,CartItem
 
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ['id', 'user', 'category',
                  'name', 'description', 'price', 'stock', 'image']
        read_only_fields = ['id', 'user']


from .models import CartItem

class CartSerializer(serializers.ModelSerializer):
    """Serializer for the order object."""

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user','created_at', 'updated_at']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'quantity']
        read_only_fields = ['id', 'cart']


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    product_data = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_data', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the order object."""
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'address','pays', 'total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
  