import random
import requests
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

User = get_user_model()

# --- Serializers ---
class LoginCodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=6, 
        min_length=6, 
        help_text="Telegramnan kelgen 6 sanlı kod"
    )

# --- Views ---

class TelegramWebhookView(APIView):
    """Telegramnan kelgen xabarlardı qayta islew"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # 1. Qáwipsizlik tekseriw (X-Telegram-Bot-Api-Secret-Token)
        tg_secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if settings.TG_SECRET and tg_secret != settings.TG_SECRET:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        update = request.data
        if "message" not in update:
            return Response({"status": "no message"})

        message = update["message"]
        chat_id = message["chat"]["id"]

        # 2. /start komandası kelse - Kontakt soraw túyresin jiberiw
        if "text" in message and message["text"] == "/start":
            self.send_contact_button(chat_id)
        
        # 3. Kontakt (telefon nomer) kelse - Kod generaciya qılıw
        elif "contact" in message:
            contact = message["contact"]
            # Telefon nomerdi formatlaw (+ belgisin alıp taslaw)
            phone_number = str(contact["phone_number"]).replace('+', '')

            # 6 sanlı unikal kod
            code = "{:06d}".format(random.randint(0, 999999))
            
            # Keshte (cache) saqlaw (phone_number ataması menen)
            cache_data = {
                "phone_number": phone_number,
                "chat_id": chat_id,
                "first_name": contact.get("first_name", ""),
                "last_name": contact.get("last_name", ""),
            }
            cache.set(f"auth_{code}", cache_data, timeout=120)

            self.send_tg_msg(chat_id, f"Sizdiń tastıyqlaw kodińiz: {code}\nBul kod 2 minut dawamında aktiv.")
        
        return Response({"status": "ok"})

    def send_contact_button(self, chat_id):
        """Telefon nomerdi jiberiw túyresin kórsetiw"""
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "Dizimnen ótiw ushın telefon nomerińizdi jiberiń:",
            "reply_markup": {
                "keyboard": [[{"text": "📞 Telefon nomerdi jiberiw", "request_contact": True}]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            }
        }
        requests.post(url, json=payload, timeout=5)

    def send_tg_msg(self, chat_id, text):
        """Ápiwayı tekst jiberiw hám klaviaturanı alıp taslaw"""
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "reply_markup": {"remove_keyboard": True}
        }
        requests.post(url, json=payload, timeout=5)


class LoginWithCodeView(APIView):
    """Kodtı JWT tokenge almastırıw"""
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginCodeSerializer

    @extend_schema(
        request=LoginCodeSerializer,
        responses={200: dict, 400: dict},
        description="Telegramnan alınǵan kod arqalı login qılıw"
    )
    def post(self, request):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        
        code = ser.validated_data['code']
        cache_key = f"auth_{code}"
        data = cache.get(cache_key)

        if not data:
            return Response({"error": "Kod nadurıs yamasa waqtı ótken"}, status=status.HTTP_400_BAD_REQUEST)

        # Paydalanıwshını alıw yamasa jańadan jaratıw
        user, created = User.objects.get_or_create(
            phone_number=data['phone_number'], # Cache-den 'phone_number' gilti menen alıw
            defaults={
                'telegram_id': data.get('chat_id'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'email': f"tg_{data['phone_number']}@dukan.uz", # Unikal email
                'role': 'KLIENT' # Custom User modelińizdegi default rol
            }
        )
        if not user.telegram_id:
            user.telegram_id = data.get('chat_id')
            user.save()
                
        # Kod isletildi - keshten óshiremiz
        cache.delete(cache_key)
        
        # JWT Token jaratıw
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "phone_number": user.phone_number,
            "is_new_user": created
        }, status=status.HTTP_200_OK)