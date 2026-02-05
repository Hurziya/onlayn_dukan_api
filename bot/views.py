import random
import requests
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

User = get_user_model()

class TelegramWebhookView(APIView):
    """Telegramnan kelgen xabarlardı qabıllaw hám kod jiberiw"""
    authentication_classes = []
    permission_classes = []

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        update = request.data
        if "message" in update:
            message = update["message"]
            chat_id = message["chat"]["id"]
            
            if "text" in message and message["text"] == "/start":
                self.send_contact_request(chat_id)
            
            elif "contact" in message:
                contact = message["contact"]
                phone_number = contact["phone_number"].replace('+', '') # + belgisin alıp taslaw
                
                code = str(random.randint(100000, 999999))
                
                cache_data = {
                    "phone_number": phone_number,
                    "first_name": contact.get("first_name", ""),
                    "last_name": contact.get("last_name", ""),
                }
                cache.set(f"auth_code_{code}", cache_data, timeout=120)
                
                self.send_message(chat_id, f"Sizdiń tastıyqlaw kodıńız: {code}\nBul kod 2 minut dawamında aktiv boladı.")
        
        return Response({"status": "ok"})

    def send_contact_request(self, chat_id):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Dizimnen ótiw ushın tómendegi túymeni basıp telefon nomerińizdi jiberiń:",
            "reply_markup": {
                "keyboard": [[{"text": "📞 Telefon nomerdi jiberiw", "request_contact": True}]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
        }
        requests.post(url, json=payload)

    def send_message(self, chat_id, text):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text, "reply_markup": {"remove_keyboard": True}})


class LoginWithCodeView(APIView):
    """Bot bergen kod arqalı sistemaga kiriw hám JWT alıw"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Kod kiritiliwi shárt"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_data = cache.get(f"auth_code_{code}")
        if not cache_data:
            return Response({"error": "Kod nadurıs yamasa waqtı ótken"}, status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = cache_data.get("phone_number")
        
        # Paydalanıwshını bazadan izlew yamasa jańadan jaratıw
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'first_name': cache_data.get("first_name", ""),
                'last_name': cache_data.get("last_name", ""),
            }
        )
        
        # Kod isletilgennen keyin keshten óshiriw
        cache.delete(f"auth_code_{code}")
        
        # JWT Token jaratıw
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "phone_number": phone_number,
            "is_new_user": created
        })