from rest_framework import serializers
from .models import Category, Product, Card, CardItem, Order, OrderItem, Review

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data if obj.children.exists() else []

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    final_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'category_name', 'name', 'slug', 'price', 'discount_price', 'final_price', 'stock', 'image']

class CardItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CardItem
        fields = ['id', 'product', 'quantity', 'item_total_price']

    def get_item_total_price(self, obj):
        return obj.quantity * obj.product.final_price

class CardSerializer(serializers.ModelSerializer):
    items = CardItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        return sum(item.quantity * item.product.final_price for item in obj.items.all())

class AddToCardSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)


class CheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(required=True)
    card_item_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        allow_empty=False
    )

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'address', 'items', 'created_at']

    def get_items(self, obj):
        return [{"product": i.product.name, "qty": i.quantity, "price": i.price} for i in obj.items.all()]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['user']