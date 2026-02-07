from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.test import TestCase

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list') 
        self.me_url = reverse('user-manage-profile') 
        self.logout_url = reverse('user-logout') 
        
        self.user_data = {
            "phone_number": "+998901112233",
            "email": "testuser@gmail.com", # Shın email
            "password": "password123",
            "first_name": "Atabek",
            "last_name": "Jalgasov"
        }
        
        self.user = User.objects.create_user(
            phone_number="+998905556677",
            email="existing@gmail.com",
            password="testpassword"
        )

    def test_create_user_manager(self):
        """UserManager avtomat email jaratpawın (None bolıwın) tekseriw"""
        user = User.objects.create_user(phone_number="+998900000000", password="pass")
        self.assertEqual(user.phone_number, "+998900000000")
        self.assertIsNone(user.email) # Endi bul jer None bolıwı kerek

    def test_create_superuser_manager(self):
        """Superuser jaratıwda email mindetliligi"""
        admin = User.objects.create_superuser(
            phone_number="+998909999999", 
            email="admin@gmail.com", 
            password="adminpass"
        )
        self.assertTrue(admin.is_superuser)

    def test_user_registration(self):
        """API arqalı dizimnen ótiw"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], self.user_data['email'])

    # ... (basqa profil, logout testleri ózgerissiz qaladı)

class UserSignalTest(TestCase):
    def test_welcome_email_signal_sent(self):
        """Email kiritilse xat ketiwi kerek"""
        mail.outbox = []
        User.objects.create_user(
            phone_number="+998908887766",
            email="realuser@gmail.com",
            password="password123"
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_email_not_sent_if_no_email(self):
        """Email kiritilmese (None bolsa) xat ketpesligi kerek"""
        mail.outbox = []
        # UserManager bul jerde email-dı None qıladı
        User.objects.create_user(
            phone_number="+998904445566",
            password="password123"
        )
        # Email None bolǵanı ushın signaldaǵı 'if instance.email' islemeydi
        self.assertEqual(len(mail.outbox), 0)