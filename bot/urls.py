from django.urls import path
from .views import TelegramWebhookView, LoginWithCodeView

urlpatterns = [
    path('webhook/', TelegramWebhookView.as_view(), name='telegram-webhook'),
    path('login-with-code/', LoginWithCodeView.as_view(), name='login-with-code'),
]