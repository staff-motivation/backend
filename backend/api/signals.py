from uuid import uuid4

from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from djoser.signals import user_registered


@receiver(user_registered)
def send_email_with_confirmation_code(request):
    subject = 'Comfirmartion code for Staff-motivation'
    message = (
        'Enter the confirmation code on the site to activate your account'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    # указываем почтовый ящик от которого будет приходитьс рассылка
    mail_to = request.data.get('email')
    confirmation_code = uuid4().hex
    print(f'Sending email to: {mail_to}')

    send_mail(
        subject,
        f'{message} = {confirmation_code}',
        from_email,
        [mail_to],
        fail_silently=False,
    )
    print('Email sent successfully')
