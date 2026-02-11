from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm  # Formalardı import etemiz

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Arnawlı formalardı qosamız
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    list_display = ('phone_number', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    ordering = ('phone_number',)

    # Paydalanıwshı maǵlıwmatın ózgertiw beti ushın
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Jeke maǵlıwmatlar', {'fields': ('first_name', 'last_name', 'email', 'address',  'role', 'telegram_id')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Waqıtlar', {'fields': ('last_login', 'date_joined')}),
    )

    # Jańa paydalanıwshı qosıw beti ushın (Password bul jerde avtomat 2 ret soraladı)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'address', 'is_active', 'is_staff'),
        }),
    )

    # Phone_number field USERNAME_FIELD bolǵanı ushın kerek
    filter_horizontal = ('groups', 'user_permissions',)