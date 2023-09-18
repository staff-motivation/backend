from django.conf import settings
from django.db import models

# from users.models import User


class News(models.Model):
    """News model"""

    news_author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news'
    )

    news_title = (models.TextField(verbose_name='Заголовок новости'),)
    news_image = models.ImageField('Картинка новости', blank=True)
    news_text = models.TextField(verbose_name='Текст новости')
    news_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации новости',
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        # Если необходимо добавить проверку уникальности новости
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['news_title', 'news_author'],
        #         name='unique_news_title'
        #     )
        # ]


class Comment(models.Model):
    """News Comment model"""

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        db_column='news',
        related_name='comments',
        verbose_name='Новость',
    )
    comment_text = models.TextField(verbose_name='Текст комментария')
    comment_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='comment_author',
        related_name='comments',
        verbose_name='Автор комментария',
    )
    comment_date = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
