from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError, models
from django.db.models import UniqueConstraint
from rest_framework import serializers

from backend.settings import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME
from department.models import Department


class UserRole(models.TextChoices):
    """Роли пользователей."""

    USER = 'user', 'Пользователь'
    TEAMLEADER = 'teamleader', 'Тимлид'
    ADMIN = 'admin', 'Администратор'


class Position(models.TextChoices):
    """Квалификация."""

    JUNIOR = 'junior', 'Junior'
    MIDDLE = 'middle', 'Middle'
    SENIOR = 'senior', 'Senior'


class Hardskill(models.Model):
    """
    Модель хардскиллов.
    """

    name = models.CharField(
        verbose_name='Хардскилл',
        help_text='Введите профессиоанльный навык/хардскилл',
        max_length=MAX_LENGTH_USERNAME,
        blank=False,
    )

    class Meta:
        verbose_name = 'Хардскилл'
        verbose_name_plural = 'Хардскиллы'

    def __str__(self):
        return self.name


class Contact(models.Model):
    """
    Модель контактов.
    """

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='Contact'
    )
    contact_type = models.CharField(max_length=50)
    link = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.user.first_name} - {self.contact_type}: {self.link}'


class CustomUserManager(BaseUserManager):
    """
    Кастомная настройка создания пользователя.
    В случае создания обычного юзера по умолчанию
    отключены флаги is_staff/is_superuser/is_active.
    Также действует обязательная проверка на наличие
    указанной почты при регистрации. В случае если
    регистрируется суперпользователь, то выше
    перечисленные флаги включены.
    """

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        if not email:
            raise serializers.ValidationError(
                'Поле email обязательно к заполнению'
            )

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError as e:
            raise ValueError(
                f'Ошибка при создании пользователя: {str(e)}'
            ) from e

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель для User. Параметры полей.
    """

    username = None
    department = models.ForeignKey(
        Department,
        verbose_name='Подразделение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_department',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/%Y/%m/%d',
        blank=True,
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
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите вашу фамилию',
        blank=False,
    )
    birthday = models.DateField(
        verbose_name='Дата рождения',
        help_text='Введите вашу дату рождения',
        blank=True,
        null=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text='Введите пароль',
        max_length=MAX_LENGTH_USERNAME,
        blank=False,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(_[0]) for _ in UserRole.choices),
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    position = models.CharField(
        verbose_name='Уровень должности',
        max_length=max(len(_[0]) for _ in Position.choices),
        choices=Position.choices,
        default=Position.JUNIOR,
    )
    experience = models.IntegerField(
        verbose_name='Рабочий стаж в команде', default=1
    )
    reward_points = models.PositiveIntegerField(
        verbose_name='Баллы', default=0
    )
    is_staff = models.BooleanField(
        verbose_name='Является ли пользователь персоналом', default=False
    )
    is_active = models.BooleanField(
        verbose_name='Активен ли пользователь', default=False
    )
    hardskills = models.ManyToManyField(Hardskill, through='UserHardskill')
    achievements = models.ManyToManyField(
        'Achievement', through='UserAchievement'
    )
    contacts = models.ManyToManyField(
        Contact,
        through='UserContact',
        blank=True,
        related_name='user_contacts',
    )
    completed_tasks_count = models.PositiveIntegerField(default=0)
    reward_points_for_current_month = models.IntegerField(default=0)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-reward_points', 'email')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.last_name} {self.first_name}'

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


class UserContact(models.Model):
    """
    Промежуточная модель для пользовательских контаков.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_contacts'
    )
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} - {self.contact.contact_type}'


class UserHardskill(models.Model):
    """
    Промежуточная модель для хард скиллов пользователей.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='user_hardskill',
    )
    hardskill = models.ForeignKey(
        Hardskill, verbose_name='Хард скилл', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Профессиональный навык пользователя'
        verbose_name_plural = 'Профессиональные навыки пользователя'
        constraints = [
            UniqueConstraint(
                fields=('user', 'hardskill'), name='unique hardskill for user'
            )
        ]

        def __str__(self):
            return f'{self.user.first_name} - {self.hardskill}'


class Achievement(models.Model):
    """
    Модель достижений пользователей.
    """

    name = models.CharField(
        verbose_name='Достижение',
        help_text='Введите достижение',
        max_length=MAX_LENGTH_USERNAME,
        blank=False,
    )
    value = models.PositiveIntegerField(
        verbose_name='Ценность',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/achievements/%Y/%m/%d',
        blank=True,
    )
    description = models.CharField(
        verbose_name='Описание достижения',
        max_length=MAX_LENGTH_USERNAME,
        blank=True,
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """
    Промежуточная модель для достижений пользователей.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='user_achievement',
    )
    achievement = models.ForeignKey(
        Achievement, verbose_name='Достижение', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователя'
        constraints = [
            UniqueConstraint(
                fields=('user', 'achievement'),
                name='unique achievement for user',
            )
        ]

        def __str__(self):
            return f'{self.user.first_name} - {self.achievement}'
