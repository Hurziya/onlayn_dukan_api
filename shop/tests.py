from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category, Product, Card, CardItem, Order, OrderItem

User = get_user_model()

class ECommerceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='+998901234567',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Elektronika", slug="elektronika")
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
        url = reverse('category-list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], "Telefon")

    def test_add_to_card(self):
        url = reverse('card-add-to-card')
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CardItem.objects.count(), 1)

    def test_checkout_process(self):
        card, _ = Card.objects.get_or_create(user=self.user)
        CardItem.objects.create(card=card, product=self.product, quantity=3)
        url = reverse('order-checkout')
        data = {"address": "Nukus"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_add_review(self):
        url = reverse('product-add-review', kwargs={'pk': self.product.id})
        data = {"rating": 5, "comment": "Zor!"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)