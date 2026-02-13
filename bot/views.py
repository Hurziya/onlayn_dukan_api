import random
import requests
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()

class LoginCodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=6, 
        min_length=6, 
        help_text="Telegramnan kelgen 6 sanlı tastıyqlaw kodı"
    )


@method_decorator(csrf_exempt, name='dispatch')
@extend_schema(exclude=True)
class TelegramWebhookView(APIView):
    """
    Telegram Bot Webhook: Kontakt qabıllaw hám kod jiberiw.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        tg_secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if settings.TG_SECRET and tg_secret != settings.TG_SECRET:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        update = request.data
        if "message" not in update:
            return Response({"status": "no message"})

        message = update["message"]
        chat_id = message["chat"]["id"]

        # 1. Start komandası
        if "text" in message and message["text"] == "/start":
            self.send_contact_button(chat_id)
        
        # 2. Kontakt (Telefon nomer) jiberilgende
        elif "contact" in message:
            contact = message["contact"]
            phone_number = str(contact["phone_number"])
            
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number

            # 6 sanlı kod jaratıw
            code = f"{random.randint(100000, 999999)}"
            
            cache_data = {
                "phone_number": phone_number,
                "chat_id": chat_id,
                "first_name": contact.get("first_name", ""),
                "last_name": contact.get("last_name", ""),
            }
            
            # Kodtı 5 minutqa cache-ge saqlaw
            cache.set(f"auth_{code}", cache_data, timeout=300)

            self.send_tg_msg(chat_id, f"✅ Sizdiń tastıyqlaw kodińiz: {code}\n\nBul kod 5 minut dawamında aktiv boladı.")
        
        return Response({"status": "ok"})

    def send_contact_button(self, chat_id):
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Dizimnen ótiw ushın tómendegi túyme arqalı telefon nomerińizdi jiberiń:",
            "reply_markup": {
                "keyboard": [[{"text": "📞 Telefon nomerdi jiberiw", "request_contact": True}]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
        }
        requests.post(url, json=payload, timeout=5)

    def send_tg_msg(self, chat_id, text):
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "reply_markup": {"remove_keyboard": True}
        }
        requests.post(url, json=payload, timeout=5)


@extend_schema_view(
    post=extend_schema(
        tags=['Auth'],
        summary="Kod arqalı login",
        request=LoginCodeSerializer,
        description="Telegram bot jibergen 6 sanlı kod arqalı Token (JWT) alıw."
    )
)
class LoginWithCodeView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        ser = LoginCodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        code = ser.validated_data['code']
        data = cache.get(f"auth_{code}")

        if not data:
            return Response(
                {"error": "Kod nadurıs yamasa waqtı ótken"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            phone_number=data['phone_number'], 
            defaults={
                'telegram_id': data.get('chat_id'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'role': 'KLIENT'
            }
        )
        
        # Telegram ID-sin jańalap qoyıw (eger ózgergen bolsa)
        if user.telegram_id != data.get('chat_id'):
            user.telegram_id = data.get('chat_id')
            user.save()
                
        # Paydalanılǵan kodtı cache-den óshiriw
        cache.delete(f"auth_{code}")
        
        # JWT Token jaratıw
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "is_new": created
            }
        }, status=status.HTTP_200_OK)   