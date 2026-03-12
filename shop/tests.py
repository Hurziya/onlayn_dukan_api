# from django.urls import reverse
# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from .models import Category, Product, Card, CardItem, Order, OrderItem

# User = get_user_model()

# class ShopAPITests(APITestCase):

#     def setUp(self):
#         # 1. Paydalanıwshılar jaratıw
#         self.user = User.objects.create_user(phone_number="+998901112233", password="testpassword123")
#         self.client.force_authenticate(user=self.user)

#         # 2. Kategoriya hám Ónim jaratıw
#         self.category = Category.objects.create(name="Elektronika", slug="elektronika")
#         self.product = Product.objects.create(
#             category=self.category,
#             name="Smartfon",
#             slug="smartfon",
#             price=1000,
#             discount_price=900,
#             stock=10,
#             is_active=True
#         )

#     ## --- SEBET TESTLERI ---

#     def test_add_to_card(self):
#         """Sebetke ónim qosıwdı tekseriw"""
#         url = reverse('card-add')
#         data = {"product_id": self.product.id, "quantity": 2}
#         response = self.client.post(url, data)
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(CardItem.objects.count(), 1)
    
#         self.assertEqual(CardItem.objects.first().quantity, 3)

#     def test_cart_total_price(self):
#         """Sebettegi ulıwma bahadanıń durıs esaplanıwın tekseriw"""
#         cart = Card.objects.create(user=self.user)
#         CardItem.objects.create(card=cart, product=self.product, quantity=2) # 900 * 2 = 1800
        
#         url = reverse('card-my-card')
#         response = self.client.get(url)
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(float(response.data['total_cart_price']), 1800.0)

#     ## --- BUYIRTPA (ORDER) TESTLERI ---

#     def test_checkout_logic(self):
#         """Checkout waqtında stoktıń kemeyiwi hám sebettiń tazalanıwı"""
#         cart = Card.objects.create(user=self.user)
#         item = CardItem.objects.create(card=cart, product=self.product, quantity=3)
        
#         url = reverse('order-checkout')
#         data = {
#             "address": "Nukus, Raycentr",
#             "card_item_ids": [item.id]
#         }
        
#         response = self.client.post(url, data)
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
        
#         # Stok kemeygenin tekseriw (10 - 3 = 7)
#         self.product.refresh_from_db()
#         self.assertEqual(self.product.stock, 7)
        
#         # Sebet bosalǵanın tekseriw
#         self.assertEqual(CardItem.objects.count(), 0)
        
#         # Buyırtpa jaratılǵanın tekseriw
#         self.assertEqual(Order.objects.count(), 1)
#         self.assertEqual(float(Order.objects.first().total_price), 2700.0) # 900 * 3

#     ## --- PIKIRLER (REVIEW) TESTLERI ---

#     def test_review_permission_fail(self):
#         """Satıp almaǵan ónimge pikir qaldıra almawı kerek"""
#         url = reverse('review-list')
#         data = {
#             "product": self.product.id,
#             "rating": 5,
#             "comment": "Jaqsı eken!"
#         }
#         response = self.client.post(url, data)
        
#         # 400 Bad Request kútemiz, sebebi perform_create-de ValidationError bar
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_review_permission_success(self):
#         """Satıp alǵan hám tólegen (PAID) ónimge pikir qaldıra alıwı"""
#         # Buyırtpa jaratıw hám statusın PAID qılıw
#         order = Order.objects.create(user=self.user, total_price=900, status='PAID', address="test")
#         OrderItem.objects.create(order=order, product=self.product, price=900, quantity=1)
        
#         url = reverse('review-list')
#         data = {
#             "product": self.product.id,
#             "rating": 5,
#             "comment": "Zamanagóy smartfon!"
#         }
#         response = self.client.post(url, data)
        
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)