import re
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

User = get_user_model()

class TelegramAuthFlowTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.webhook_url = reverse('webhook')
        self.login_url = reverse('login')
        # Test ushın turaqlı secret token
        self.secret_token = "super_secret_token_123"

    @patch('requests.post')
    def test_full_auth_flow(self, mock_post):
        """Tolıq login protsessi: Webhook -> Cache -> Login"""
        
        # 1. Webhook-qa kontakt jiberiw
        payload = {
            "message": {
                "chat": {"id": 12345678},
                "contact": {
                    "phone_number": "+998901234567",
                    "first_name": "Alisher"
                }
            }
        }
        
        headers = {'HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN': self.secret_token}
        
        with override_settings(TG_SECRET=self.secret_token, TG_TOKEN="123:ABC"):
            response = self.client.post(self.webhook_url, payload, format='json', **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Mock-tan jiberilgen kodtı alıw
        args, kwargs = mock_post.call_args
        sent_json = kwargs['json']
        sent_text = sent_json['text']
        extracted_code = re.findall(r'\d{6}', sent_text)[0]

        # 2. LoginView-dı testlew
        login_response = self.client.post(self.login_url, {"code": extracted_code}, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        
        # 3. User bazada bar ekenin tekseriw
        self.assertTrue(User.objects.filter(phone_number="+998901234567").exists())

    def test_webhook_unauthorized(self):
        """Nadurıs token menen 403 qaytarıwın tekseriw"""
        headers = {'HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN': 'wrong_token'}
        
        with override_settings(TG_SECRET=self.secret_token):
            response = self.client.post(self.webhook_url, {"message": "hi"}, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)