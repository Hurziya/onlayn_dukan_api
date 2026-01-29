from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Category, Product, Card, CardItem, Order

class ECommerceTests(APITestCase):
    """
    Sistemanıń tiykarǵı funksionalın tekseriw ushın testler toplamı.
    """

    def setUp(self):
        """Test baslanıwdan aldın kerekli maǵlıwmatlardı jaratıw."""
        # 1. Paydalanıwshı jaratıw
        self.user_data = {
            "phone_number": "+998901234567",
            "password": "testpassword123",
            "first_name": "Atabek",
            "last_name": "Joldasbaev"
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # 2. Admin jaratıw
        self.admin = User.objects.create_superuser(
            phone_number="+998907654321", 
            password="adminpassword",
            first_name="Admin",
            last_name="Boss"
        )

        # 3. Kategoriya hám Ónim jaratıw
        self.category = Category.objects.create(name="Elektronika", slug="elektronika")
        self.product = Product.objects.create(
            category=self.category,
            name="Samsung S23",
            slug="samsung-s23",
            price=1000.00,
            stock=10,
            is_active=True
        )
        
        # Autentifikaciya (Login)
        self.client.force_authenticate(user=self.user)

    # --- USER TESTS ---
    def test_user_registration(self):
        """Jańa paydalanıwshı dizimnen ótiwin tekseriw."""
        self.client.logout() # Dizimnen shıǵıp turamız
        url = reverse('user-list') # /users/
        data = {
            "phone_number": "+998990001122",
            "password": "newpassword123",
            "first_name": "Ali",
            "last_name": "Valiev"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_get_me_profile(self):
        """/users/me/ endpointı durıs isleytuǵının tekseriw."""
        url = reverse('user-manage-profile') # /users/me/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)

    # --- PRODUCT TESTS ---
    def test_get_product_list(self):
        """Ónimler dizimin alıwdı tekseriw."""
        url = reverse('product-list') # /products/
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pagination sebepli 'results' ishinde boladı
        self.assertTrue(len(response.data['results']) > 0)

    # --- CART TESTS ---
    def test_add_to_card(self):
        """Sebetke ónim qosıwdı tekseriw."""
        url = reverse('card-add-to-card') # /card/add_to_card/
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CardItem.objects.filter(product=self.product).first().quantity, 2)

    def test_add_to_card_out_of_stock(self):
        """Qoymada joq muǵdarda ónim qospaqshı bolǵanda qáte beriwini tekseriw."""
        url = reverse('card-add-to-card')
        data = {"product_id": self.product.id, "quantity": 50} # Qoymada tek 10 dana bar
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    # --- ORDER TESTS ---
    def test_checkout_process(self):
        """Buyırtpa beriw (checkout) processin tolıq tekseriw."""
        # 1. Aldın sebetke ónim qosamız
        card, _ = Card.objects.get_or_create(user=self.user)
        CardItem.objects.create(card=card, product=self.product, quantity=2)

        # 2. Checkout mánziline POST jiberemiz
        url = reverse('order-checkout') # /orders/checkout/
        data = {"address": "Nukis qalası, mánzil №1"}
        response = self.client.post(url, data)

        # 3. Nátiyjelerdi tekseriw
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Qoymadaǵı ónim sanı kemeygenin tekseriw (10 - 2 = 8)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # Buyırtpa jaratılǵanın tekseriw
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

        # Sebet tazalanǵanın tekseriw
        self.assertEqual(card.items.count(), 0)

    # --- PERMISSION TESTS ---
    def test_admin_only_can_create_category(self):
        """Admin bolmaǵan user kategoriya jarata almawın tekseriw."""
        url = reverse('category-list')
        data = {"name": "Test Cat", "slug": "test-cat"}
        
        # Ápiwayı user menen urınıp kóremiz
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admin menen urınıp kóremiz
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



    def test_logout(self):
        """Logout processin tekseriw."""
        # Aldın login bolıp refresh token alamız
        login_url = reverse('token_obtain_pair')
        login_response = self.client.post(login_url, {
            "phone_number": self.user_data["phone_number"],
            "password": self.user_data["password"]
        })
        refresh_token = login_response.data['refresh']

        # Logout-qa jiberemiz
        logout_url = reverse('user-logout')
        response = self.client.post(logout_url, {"refresh": refresh_token})
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)