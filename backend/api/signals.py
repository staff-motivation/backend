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
        message_for_admin = (
            f'Добавлен новый сотрудник - {user.email} '
            'Присвойте ему токен для дальнейшей работы.'
        )
        from_email = 'noreply@example.com'
        # указываем почтовый ящик от которого будет приходитьс рассылка
        recipient_list = [user.email]
        stuff_recipient_list = ['admin@example.com']
        print(f"Sending email to: {recipient_list}")

        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully")

        send_mail(subject, message_for_admin, from_email, stuff_recipient_list)
        print("Email-admin sent successfully")

    except Exception as e:
        print(f"Error sending email: {e}")
