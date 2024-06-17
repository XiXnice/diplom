from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task()
def send_email(title, message,  from_email, email,):
    msg = EmailMultiAlternatives(
        subject=title,
        body=message,
        from_email=from_email,
        to=email
    )
    msg.send()