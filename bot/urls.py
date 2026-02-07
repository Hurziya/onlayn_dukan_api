from django.urls import path
from .views import TelegramWebhookView, LoginWithCodeView

urlpatterns = [
    path('webhook/', TelegramWebhookView.as_view(), name='webhook'),
    path('login/', LoginWithCodeView.as_view(), name='login'),
]