from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm  

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    list_display = ('phone_number', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)


    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Jeke maǵlıwmatlar', {'fields': ('first_name', 'last_name', 'address',  'role', 'telegram_id')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Waqıtlar', {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'first_name', 'last_name', 'password1', 'password2', 'role', 'address', 'is_active', 'is_staff'),
        }),
    )


    filter_horizontal = ('groups', 'user_permissions',)


