from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    # Jaratılǵanda (created) hám email kiritilgen bolsa ǵana xat jiberemiz
    if created and instance.email:
        subject = 'Onlayn Dukan - Xosh keldińiz!'
        message = f'Sálem {instance.first_name or "Paydalanıwshı"}, dukanımızǵa xosh keldińiz!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        try:
            send_mail(subject, message, email_from, recipient_list, fail_silently=True)
        except Exception:
            pass