from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Category, Product, Order, OrderItem, Card, CardItem, Review
from django.db.models import Avg

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):  
    """Kategoriyalardı basqarıw hám slug-dı avtomat toltyrıw."""
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)
    ordering = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__phone_number')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'get_avg_rating')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def get_avg_rating(self, obj):
        result = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(result, 1) if result else "Pikir joq"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Buyırtpalardı baqlaw hám statusın basqarıw."""
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    search_fields = ('user__phone_number',)
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Buyırtpa ishindegi konkret ónimler dizimi."""
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__user__phone_number', 'product__name')
    list_filter = ('order__status',)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Paydalanıwshı sebetlerin kóriw."""
    list_display = ('user',)
    search_fields = ('user__phone_number',)


@admin.register(CardItem)
class CardItemAdmin(admin.ModelAdmin):
    """Sebettegi elementlerdi baqlaw."""
    list_display = ('card', 'product', 'quantity')
    search_fields = ('card__user__phone_number', 'product__name')
    list_filter = ('card__user__role',)