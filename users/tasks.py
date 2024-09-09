from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

token_generator = PasswordResetTokenGenerator()


def send_invite(user):
    subject = "Activar cuenta - Educación Transparente"
    from_email = settings.EMAIL_FROM
    to = user.email
    context = {
        "user": user,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": token_generator.make_token(user),
        "base_url": "http://localhost:8000",
    }
    html_content = render_to_string("users/emails/password_reset_email.html", context)
    plain_message = strip_tags(html_content)
    send_mail(
        subject,
        plain_message,
        from_email,
        [to],
        html_message=html_content,
    )
