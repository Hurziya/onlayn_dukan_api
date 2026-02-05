from django.apps import AppConfig
import sys

class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        if 'runserver' in sys.argv:
            self.set_telegram_webhook()

    def set_telegram_webhook(self):
        import requests
        from django.conf import settings
        
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
        
        if not token or not webhook_url:
            print("Eskertiw: TELEGRAM_BOT_TOKEN yamasa TELEGRAM_WEBHOOK_URL settings.py-da tabılmadı. Webhook ornatılmadı.")
            return

        url = f"https://api.telegram.org/bot{token}/setWebhook"
        try:
            response = requests.post(url, json={"url": webhook_url})
            if response.status_code == 200:
                print(f"Telegram Webhook tabıslı ornatıldı: {webhook_url}")
            else:
                print(f"Telegram Webhook ornatıp bolmadı: {response.text}")
        except Exception as e:
            print(f"Telegram Webhook sazlawı qáte: {e}")