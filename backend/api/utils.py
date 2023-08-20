# from djoser import create_token
# from django.core.mail import send_mail
#
# def send_activation_email(user):
#     activation_token = create_token(user)
#     activation_url = f"#/activate/{user.pk}/{activation_token}"  # Замените на ваш URL-путь активации
#     subject = "Активация аккаунта"
#     message = f"Для активации аккаунта перейдите по ссылке: {activation_url}"
#     from_email = "noreply@example.com"
#     recipient_list = [user.email]
#     send_mail(subject, message, from_email, recipient_list)