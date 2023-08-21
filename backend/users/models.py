from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.db import models

from backend.settings import MAX_LENGTH_USERNAME, MAX_LENGTH_EMAIL


class UserRole(models.TextChoices):
    """ Роли пользователей. """
    USER = 'user', 'Пользователь'
    TEAMLEADER = 'teamleader', 'Тимлид'
    ADMIN = 'admin', 'Администратор'


class Position(models.TextChoices):
    """ Квалификация. """
    JUNIOR = 'junior', 'Junior'
    MIDDLE = 'middle', 'Middle'
    SENIOR = 'senior', 'Senior'


class DepartmentName(models.TextChoices):
    """ Название подразделения. """
    BACKEND = 'Backend'
    FRONTEND = 'Frontend'
    UX_UI = 'UX_UI'
    QA = 'QA'
    NONE = 'None'


class AllowedEmail(models.Model):
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Разрешенные email"
        verbose_name_plural = "Разрешенные email"

    def __str__(self):
        return self.email


class Department(models.Model):
    name = models.CharField(
        verbose_name='Подразделение',
        max_length=max(len(_[0]) for _ in UserRole.choices),
        choices=DepartmentName.choices,
        default=DepartmentName.NONE
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание подразделения',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/department/%Y/%m/%d',
        blank=True
    )

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class Group(models.Model):
    """
    Модель для групп пользователей.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите название группы'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание группы'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/groups/%Y/%m/%d',
        blank=True
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return str(self.name)


class Bonus(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите название бонуса'
    )
    bonus_points = models.IntegerField(
        verbose_name='Бонусные очки'
    )
    privilege = models.TextField(
        verbose_name='Привилегии',
    )

    class Meta:
        verbose_name = 'Бонус'
        verbose_name_plural = 'Бонусы'

    def __str__(self):
        return str(self.name)


class UserRating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_ratings')
    kpi_name = models.CharField(
        verbose_name='Название KPI',
        max_length=MAX_LENGTH_USERNAME
    )
    kpi_category = models.CharField(
        verbose_name='Категория KPI',
        max_length=MAX_LENGTH_USERNAME
    )
    target = models.IntegerField(
        verbose_name='Целовой показатель KPI',
    )
    actual = models.IntegerField(
        verbose_name='Актуальный показатель KPI',
    )
    date = models.DateField(
        verbose_name='Дата выполнения задания',
    )

    def __str__(self):
        return str(self.kpi_name)

    class Meta:
        verbose_name = 'KPI показатель'
        verbose_name_plural = 'KPI показатели'


class User(AbstractUser):
    """
    Модель для User. Параметры полей.
    """
    username = models.CharField(
        verbose_name='Ник-нейм',
        max_length=MAX_LENGTH_USERNAME,
        help_text='Введите имя пользователя',
        unique=True,
        db_index=True,
        blank=False
    )
    department = models.ForeignKey(
        Department,
        verbose_name='Подразделение',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_department'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='Группа',
        related_name='users_groups',
        through='Membership',
        blank=True
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
        max_length=max(len(_[0]) for _ in UserRole.choices),
        choices=UserRole.choices,
        default=UserRole.USER
    )
    position = models.CharField(
        verbose_name='Уровень должности',
        max_length=max(len(_[0]) for _ in Position.choices),
        choices=Position.choices,
        default=Position.JUNIOR
    )
    experience = models.IntegerField(
        verbose_name='Опыт работы',
        default=1
    )
    user_rating = models.ForeignKey(
        UserRating,
        verbose_name='Рейтинг работника',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rating'
    )
    bonus = models.ForeignKey(
        Bonus,
        verbose_name='Бонусы',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_staff = models.BooleanField(
        verbose_name='Является ли пользователь персоналом',
        default=False
    )
    is_active = models.BooleanField(
        verbose_name='Активен ли пользователь',
        default=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'birthday',
        'password',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('birthday',)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"

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


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Contact')
    platform = models.CharField(max_length=50)
    link = models.URLField()

    def __str__(self):
        return f"{self.user.first_name} - {self.platform}"


class Membership(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Участник группы'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name='Группа'
    )
    date_joined = models.DateTimeField(
        verbose_name='Дата присоединения',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                name='unique_group'
            )
        ]

        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'
        ordering = ('group',)
