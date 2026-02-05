from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


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