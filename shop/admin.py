from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Card, CardItem, Review
from django.db.models import Avg


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('price',)

class CardItemInline(admin.TabularInline):
    model = CardItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'get_avg_rating')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('price', 'stock', 'is_active') # Adminniń ózinde tez ózgertiw ushın

    def get_avg_rating(self, obj):
        result = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(result, 1) if result else "—"
    get_avg_rating.short_description = 'Reyting' 


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__phone_number', 'id')
    inlines = [OrderItemInline] # Buyırtpa ishindegi ónimlerdi kórsetedi
    readonly_fields = ('created_at',)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_items_count')
    search_fields = ('user__phone_number',)
    inlines = [CardItemInline] # Sebet ishindegi ónimlerdi kórsetedi

    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = 'Ónimler sanı'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__phone_number', 'comment') 


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')


@admin.register(CardItem)
class CardItemAdmin(admin.ModelAdmin):
    list_display = ('card', 'product', 'quantity')