import random
from django.core.mail import send_mail


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(to_email, otp):
    from django.conf import settings
    send_mail(
        subject="Staff Registration OTP",
        message=f"OTP for staff registration: {otp}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to_email],
        fail_silently=False,
    )
