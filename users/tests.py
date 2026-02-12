from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserTests(APITestCase):

    def setUp(self):
        self.user_data = {
            "phone_number": "+998901234567",
            "password": "testpassword123",
            "first_name": "Atabek",
            "last_name": "Joldasov",
            "address": "Nukus qalası"
        }
        self.register_url = reverse('user-list')  
        self.me_url = reverse('user-manage-profile') 

    def test_user_registration(self):
        """Paydalanıwshı dizimnen ótiwin testlew"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().phone_number, self.user_data["phone_number"])

    def test_get_own_profile(self):
        """Paydalanıwshı óz profilin kóre alıwın testlew"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user_data["phone_number"])

    def test_update_profile(self):
        """Profil maǵlıwmatların jańalawdı testlew"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        update_data = {"first_name": "Talas", "address": "Tashkent"}
        response = self.client.patch(self.me_url, update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Talas")
        self.assertEqual(user.address, "Tashkent")

    def test_logout(self):
        """Logout procesin (tokenni blacklistke túsiriw) testlew"""
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)
        
        logout_url = reverse('user-logout')
        data = {"refresh": str(refresh)}
        
        self.client.force_authenticate(user=user)
        response = self.client.post(logout_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Siz sistemadan tabıslı shıqtıńız")

    def test_anonymous_user_cannot_see_profile(self):
        """Login bolmaǵan adam profilge kire almawın testlew"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)