from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Product, Order, OrderItem, Card, CardItem, Review

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom paydalanıwshı modelin admin panelde basqarıw ushın klass."""
    list_display = ('phone_number', 'role', 'is_staff', 'is_active')
    search_fields = ('phone_number',)
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('phone_number',)

    fieldsets = (   
        (None, {'fields': ('phone_number', 'password')}),
        ('Jeke maǵlıwmatlar', {'fields': ('first_name', 'last_name', 'address', 'role')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Waqıtlar', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('phone_number', 'password', 'role', 'address', 'is_active', 'is_staff'),
        }), 
    )


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

# ProductAdmin di jańalaw
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'get_avg_rating')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def get_avg_rating(self, obj):
        from django.db.models import Avg
        result = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(result, 1) if result else "Pikir joq"
    get_avg_rating.short_description = "Reyting"


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