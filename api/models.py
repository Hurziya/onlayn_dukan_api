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
    Standart 'username' ornına 'phone_number' qollanıladı.
    """
    username = None       
    class Role(models.TextChoices): 
        ADMIN = 'ADMIN', 'Admin'
        KLIENT = 'KLIENT', 'Klient'

    role = models.CharField(max_length=15, choices=Role.choices, default=Role.KLIENT)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)

    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = ['first_name', 'last_name']  

    objects = UserManager() 

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


class Category(models.Model):
    """
    Ónimlerdi túrleri boyınsha toparlaw ushın kategoriya modeli.
    Ierarxiyalıq dúziliske iye bolıwı múmkin (parent-child).
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children') 

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Satılatın ónimler tuwralı maǵlıwmatlardı saqlawshı model.
    Baha, shegirme, qaldıq hám status maǵlıwmatların óz ishine aladı.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    stock = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Card(models.Model):
    """
    Paydalanıwshınıń jeke sebeti (karzinasi).
    Hár bir paydalanıwshıda tek bir dana aktiv sebet boladı.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Card for {self.user.phone_number}"


class CardItem(models.Model): 
    """
    Sebet ishindegi konkret ónimler hám olardıń sanı.
    Sebet hám ónimler arasındaǵı baylanıstı támiyinleydi.
    """
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


class Order(models.Model):
    """
    Satıp alıw processiniń nátiyjesi bolǵan buyırtpa modeli.
    Buyırtpanıń ulıwma summası, statusı hám jetkerip beriw mánzilin saqlaydı.
    """
    class Status(models.TextChoices): 
        PENDING = 'PENDING', 'Kutilmekte'
        PAID = 'PAID', 'Tolendi'
        SHIPPED = 'SHIPPED', 'Jiberildi'
        CANCELED = 'CANCELED', 'Biykar etildi'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.phone_number}"


class OrderItem(models.Model):
    """
    Buyırtpa ishindegi elementlerdiń 'tariyxıy' kóshirmesi.
    Ónimniń satıp alınǵan waqıttaǵı bahasın saqlap qalıw ushın kerek.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
    



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5) # 1-5 aralıǵında
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user') # Bir user bir ónimge tek bir ret pikir qaldıra aladı

    def __str__(self):
        return f"{self.user.phone_number} - {self.product.name} ({self.rating})"