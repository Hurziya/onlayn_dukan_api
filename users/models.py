from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class UserManager(BaseUserManager):
    """
    User modeli ushın arnawlı manager. 
    Telefon nomer arqılı paydalanıwshı hám superuser jaratıw logikasın basqaradı.
    """
    def create_user(self, phone_number, password=None, **extra_fields): 
        if not phone_number:
            raise ValueError('Telefon nomer jazılıwı shárt')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password) 
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields): 
        extra_fields.setdefault('is_staff', True)  
        extra_fields.setdefault('is_superuser', True)
    
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Sistemada dizimnen ótiw hám login qılıw ushın qollanılatın tiykarǵı paydalanıwshı modeli.
    Standart 'username' ornına 'phone_number' qollanıldı.
    """
    username = None       
    class Role(models.TextChoices): 
        ADMIN = 'ADMIN', 'Admin'
        KLIENT = 'KLIENT', 'Klient'

    role = models.CharField(max_length=15, choices=Role.choices, default=Role.KLIENT)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    
    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = ['first_name', 'last_name']  

    objects = UserManager() 

    def __str__(self):
        return f"{self.phone_number} ({self.role})"