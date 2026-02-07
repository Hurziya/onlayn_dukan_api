from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Telefon nomer jazılıwı shárt')
        if email:
            email = self.normalize_email(email)
        else:
            email = None # Jasalma email jaratıwdı alıp tasladıq
            
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, email, password, **extra_fields)

class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        KLIENT = 'KLIENT', 'Klient'

    username = None
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.KLIENT)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    objects = UserManager()