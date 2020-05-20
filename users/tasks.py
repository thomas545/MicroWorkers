from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from celery import shared_task
from base.send_mails import send_email

url = "http://localhost:4000/"


@shared_task
def send_confirmation_email(username, email, key):
    body = """
    Hello %s,

    click on below link to confirm your email
    Link : %saccount-confirm-email/%s 

    Micoworkers Team 
    """% (username, url, key)

    subject = "Confirmation Registeration"
    recipients = [email]
    try:
        send_email(body, subject, recipients)
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)


@shared_task
def send_reset_password_email(user):
    body = """
    Hello %s,

    click on below link to reset your password
    Link : %spassword/reset/confirm/%s/%s

    Micoworkers Team 
    """% (user.username, url, urlsafe_base64_encode(force_bytes(user.pk)), 
            default_token_generator.make_token(user))

    subject = "Confirmation Registeration"
    recipients = [user.email]
    try:
        send_email(body, subject, recipients)
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)

