from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email: 
        subject = 'Xosh keldińiz!'
        message = f'Assalamu alaykum {instance.first_name}, onlayn dúkanımızǵa xosh keldińiz!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Email jiberiwde qáte: {e}")