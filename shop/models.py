
from django.db import models
from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
# from django.core.exceptions import ValidationError


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
    Baha, shegirme, hám ónimler sanı maǵlıwmatların óz ishine aladı.
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
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name if self.product else 'Óshirilgen ónim'} (x{self.quantity})"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Rating májburiy 
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Kommentariy májburiy emes (null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.phone_number} - {self.product.name} ({self.rating})"
    
