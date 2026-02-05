from rest_framework import serializers
from .models import Category, Product, Card, CardItem, Order, OrderItem, Review



class SubCategorySerializer(serializers.ModelSerializer):
    """
    Kategoriyalardıń ishki (sub-category) dizimin kórsetiw ushın kómekshi serializer.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class CategorySerializer(serializers.ModelSerializer):
    """
    Tiykarǵı kategoriyalar hám olardıń ishindegi barlıq ishki kategoriyalardı 
    rekursiv túrde kórsetiwshi serializer.
    """
    children = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children']


class ProductSerializer(serializers.ModelSerializer):
    """
    Ónimlerdiń tolıq maǵlıwmatın kórsetiwshi serializer. 
    Shegirme bahaların esapqa alǵan halda aqırǵı 'final_price' mánisin qaytaradı.
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 
            'description', 'price', 'discount_price', 'final_price', 
            'image', 'stock', 'is_active', 'created_at'
        ]

    def get_final_price(self, obj):
        return obj.discount_price if obj.discount_price else obj.price


class CardItemSerializer(serializers.ModelSerializer):
    """
    Sebet ishindegi hárbir elementti basqarıw ushın kerek. 
    Hárbir elementtiń (ónim * sanı) ulıwma bahasınıń esaplaydı.
    """
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CardItem
        fields = ['id', 'product', 'product_id', 'quantity', 'item_total_price']

    def get_item_total_price(self, obj):
        price = obj.product.discount_price if obj.product.discount_price else obj.product.price
        return obj.quantity * price


class CardSerializer(serializers.ModelSerializer):
    """
    Paydalanıwshınıń pútin sebetin kórsetiwshi serializer. 
    Sebet ishindegi barlıq ónimlerdiń ulıwma summasın (total_cart_price) esaplaydı.
    """
    items = CardItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'user', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        items = obj.items.all()
        total = sum([
            (i.product.discount_price if i.product.discount_price else i.product.price) * i.quantity 
            for i in items
        ])
        return total


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Buyırtpa berilgen waqıttaǵı ónimler dizimi hám olardıń sol waqıttaǵı bahasın kórsetiwshi serializer.
    """
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    """
    Buyırtpalardı jaratıw hám kórsetiw ushın serializer. 
    Buyırtpa statusı hám ulıwma bahasın qáwipsizlik ushın tek oqıw (read_only) rejiminde kórsetedi.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    user_phone = serializers.ReadOnlyField(source='user.phone_number')

    class Meta:
        model = Order
        fields = ['id', 'user_phone', 'total_price', 'status', 'address', 'items', 'created_at']
        read_only_fields = ['total_price', 'status']

    def create(self, validated_data):
        return super().create(validated_data)
    

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']
        # comment avtomat túrde optional (májburiy emes) boladı