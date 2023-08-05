from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from backend.settings import MAX_LENGTH_USERNAME, MAX_LENGTH_EMAIL

from .validators import validate_username


class UserRole(models.TextChoices):
    """ Роли пользователей. """
    USER = 'user', 'Пользователь'
    TEAMLEADER = 'teamleader', 'Тимлид'
    ADMIN = 'admin', 'Администратор'


MAX_LENGTH_ROLES = max(len(_[0]) for _ in UserRole.choices)


class CustomUserManager(UserManager):
    def create_superuser(
            self,
            username, email, password, first_name, last_name,
            **extra_fields
            ):
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('first_name', first_name)
        extra_fields.setdefault('last_name', last_name)
        return super().create_superuser(
            username, email, password, **extra_fields)

    def create_user(
            self,
            username, email, password, password_confirmation,
            first_name, last_name, **extra_fields
            ):
        if password != password_confirmation:
            raise ValueError('Пароли должны совпадать!')

        extra_fields.setdefault('role', UserRole.USER)
        extra_fields.setdefault('first_name', first_name)
        extra_fields.setdefault('last_name', last_name)
        return super().create_user(
            username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель для User. Параметры полей.
    """
    username = models.CharField(
        verbose_name='Ник-нейм',
        validators=[validate_username],
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите имя пользователя',
        unique=True,
        db_index=True,
        blank=False
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/%Y/%m/%d',
        blank=True
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        help_text='Введите адрес электронной почты',
        blank=False,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите ваше имя',
        blank=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите вашу фамилию',
        blank=False
    )
    second_name = models.CharField(
        verbose_name='Отчество',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите ваш отчество',
        blank=False
    )
    birthday = models.DateField(
        verbose_name='Дата рождения',
        help_text='Введите вашу дату рождения',
        blank=False
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Введите пароль',
        max_length=MAX_LENGTH_USERNAME,
        blank=False
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=MAX_LENGTH_ROLES,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    contact = models.TextField(
        verbose_name='Контакты',
        help_text='Введите список ваших доступных контактов',
        blank=False
    )
    is_staff = models.BooleanField(
        verbose_name='Является ли пользователь персоналом',
        default=False
    )
    is_active = models.BooleanField(
        verbose_name='Активен ли пользователь',
        default=False
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'first_name', 'last_name', 'birthday',
        'second_name', 'username', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return str(self.username)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    @property
    def is_admin(self):
        """
        Свойство.
        Возвращает права админа.
        """
        return self.role == UserRole.ADMIN

    @property
    def is_teamleader(self):
        """
        Свойство.
        Возвращает права тимлида.
        """
        return self.role == UserRole.TEAMLEADER

    @property
    def is_role(self, role):
        """
        Свойство.
        Возвращает роль / права.
        """
        return self.role == role
