from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category, Product, Card, CardItem, Order, OrderItem

User = get_user_model()

class ECommerceTests(APITestCase):

    def setUp(self):
        # 1. Paydalanıwshı jaratıw (User modeli phone_number talap etedi dep esaplaymız)
        self.user = User.objects.create_user(
            password='password123',
            phone_number='+998901234567'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # 2. Kategoriya jaratıw
        self.category = Category.objects.create(name="Elektronika", slug="elektronika")
        
        # 3. Ónim jaratıw
        self.product = Product.objects.create(
            category=self.category,
            name="Telefon",
            slug="telefon",
            description="Jaqsı telefon",
            price=1000.00,
            stock=10,
            is_active=True
        )

    def test_category_list(self):
        """Kategoriyalar dizimin alıwdı tekseriw"""
        url = reverse('category-list') # URL atamaları router-ǵa baylanıslı
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_list(self):
        """Ónimler dizimi hám filtrlerdi tekseriw"""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], "Telefon")

    def test_add_to_card(self):
        """Sebetke ónim qosıwdı tekseriw"""
        url = reverse('card-add-to-card')
        data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Sebette ónim bar ekenin tekseriw
        card = Card.objects.get(user=self.user)
        self.assertEqual(CardItem.objects.filter(card=card).count(), 1)
        self.assertEqual(CardItem.objects.get().quantity, 2)

    def test_add_to_card_out_of_stock(self):
        """Qoymada joq muǵdardı qosıp kórmekshi bolǵanda qátelik shıǵıwın tekseriw"""
        url = reverse('card-add-to-card')
        data = {
            "product_id": self.product.id,
            "quantity": 15 # Stock tek 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_process(self):
        """Buyırtpa beriw (checkout) procesin tekseriw"""
        # Aldın sebetke ónim qosamız
        card, _ = Card.objects.get_or_create(user=self.user)
        CardItem.objects.create(card=card, product=self.product, quantity=3)

        url = reverse('order-checkout')
        data = {"address": "Nukus qalası, tınıshlıq kóshesi"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 1. Stock kemeygenin tekseriw (10 - 3 = 7)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

        # 2. Sebet bosalǵanın tekseriw
        self.assertEqual(card.items.count(), 0)

        # 3. Buyırtpa jaratılǵanın tekseriw
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        order = Order.objects.first()
        self.assertEqual(float(order.total_price), 3000.00)

    def test_add_review(self):
        """Ónimge pikir qaldırıwdı tekseriw"""
        url = reverse('product-add-review', kwargs={'pk': self.product.id})
        data = {
            "rating": 5,
            "comment": "Zor eken!"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.product.reviews.count(), 1)