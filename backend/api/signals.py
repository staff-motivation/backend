from django.dispatch import receiver
from djoser.signals import user_registered
from django.core.mail import send_mail


@receiver(user_registered)
def send_registration_email(sender, user, request, **kwargs):
    try:
        subject = 'Регистрация успешна'
        message = (
            'Ваш аккаунт успешно зарегистрирован.'
            'Дождитесь активации вашего аккаунта Отделом Кадров'
        )
        from_email = 'sys.motivation@gmail.com'
        recipient_list = [user.email]
        print(f"Sending email to: {recipient_list}")

        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully")

    except Exception as e:
        print(f"Error sending email: {e}")

#password - Motivate!123
#gmail - sys.motivation@gmail.com
#'noreply@example.com'
