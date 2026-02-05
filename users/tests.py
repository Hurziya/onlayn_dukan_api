from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')  # ViewSet-te POST /users/
        self.me_url = reverse('user-manage-profile') # /users/me/
        self.logout_url = reverse('user-logout') # /users/logout/
        
        self.user_data = {
            "phone_number": "+998901112233",
            "password": "password123",
            "first_name": "Atabek",
            "last_name": "Jalgasov"
        }
        
        # Testler ushın tayın paydalanıwshı
        self.user = User.objects.create_user(
            phone_number="+998905556677",
            password="testpassword",
            first_name="Test",
            last_name="User"
        )

    def test_create_user_manager(self):
        """UserManager arqalı paydalanıwshı jaratılıwın tekseriw"""
        user = User.objects.create_user(phone_number="+998900000000", password="pass")
        self.assertEqual(user.phone_number, "+998900000000")
        self.assertTrue(user.check_password("pass"))
        self.assertEqual(user.role, User.Role.KLIENT)

    def test_create_superuser_manager(self):
        """Superuser jaratılıwın tekseriw"""
        admin = User.objects.create_superuser(phone_number="+998909999999", password="adminpass")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_user_registration(self):
        """API arqalı dizimnen ótiwdi tekseriw"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phone_number'], self.user_data['phone_number'])
        # Parol qaytıp kelmewi kerek (write_only)
        self.assertNotIn('password', response.data)

    def test_manage_profile_me_get(self):
        """/users/me/ endpointi arqalı óz profilin kóriw"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)

    def test_manage_profile_me_patch(self):
        """/users/me/ arqalı profil maǵlıwmatların jańalaw"""
        self.client.force_authenticate(user=self.user)
        update_data = {"first_name": "TazaAt"}
        response = self.client.patch(self.me_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "TazaAt")

    def test_role_readonly_in_serializer(self):
        """Paydalanıwshı óz rolin ADMIN-ge ózgerte almaslıǵın tekseriw"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.me_url, {"role": "ADMIN"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.KLIENT) # Ózgermewi kerek

    def test_logout(self):
        """Logout funksiyasın tekseriw (JWT Blacklist)"""
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(self.logout_url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.data['message'], "Siz sistemadan tabıslı shıqtıńız")

    def test_list_users_permission(self):
        """Admin emes paydalanıwshı barlıq userlerdi kóre almaslıǵın tekseriw"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)