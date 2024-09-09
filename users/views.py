from django.contrib.auth import views as auth_views

from educaciontransparente import settings


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = "users/emails/password_reset_email.html"
    from_email = settings.EMAIL_HOST_USER
    subject_template_name = "users/emails/password_reset_subject.txt"
    template_name = "users/password_reset_form.html"
    title = "Restauración de contraseña"


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "users/new_password.html"


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
