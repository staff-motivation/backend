# Отправка емейлов из Django через SMTP Yandex

## Настройки settings.py

- EMAIL_HOST = 'smtp.yandex.ru'
- EMAIL_PORT = 465
- EMAIL_USE_SSL = True
- DEFAULT_FROM_EMAIL = 'youremail@yandex.ru' - емейл, который будет указан в поле "От кого".
- EMAIL_HOST_USER = 'youremail@yandex.ru' - ваш емейл на Яндексе. Как правило, идентичен предыдущему пункту.
- EMAIL_HOST_PASSWORD = 'yourownpassword' - пароль **ПРИЛОЖЕНИЯ**, который нужно создать в настройках Яндекса заранее. **Это не пароль от вашего емейла!**
- EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

## Настройки аккаунта на Яндексе

- Из страницы почты  https://mail.yandex.ru/? нажмите:
1. На шестерёнку в правом верхнем углу
2. Далее "Все настройки"
3. Далее "Почтовые программы"
4. Выставите настройки как на изображение ниже

![Screenshot (21)](https://user-images.githubusercontent.com/85797091/211198218-d1c2d452-6539-46dd-a927-583e3df190aa.png)

5. Далее перейдите на вкладку "Безопасность"
6. В тексте "Включите и создайте пароли приложений, чтобы повысить безопасность при использовании альтернативных почтовых программ."  нажмите "пароли приложений"\
7. Выберите пароль для "IMAP, POP3, SMT"
8. Придумайте название для пароля
9. Сгенерированный код добавьте в поле EMAIL_HOST_PASSWORD.

## Почтовая рассылка готова.

# Настройка pre-commit

В виртуальном окружении выполнить следующие команды:
```
git init
pre-commit install
```
- Теперь при выполнении git commit будут запускаться линтеры для проверки кода
- Настройки линтеров находятся в файле pyproject.toml
- Настройки pre-commit в файле .pre-commit-config.yaml
