from django.test import TestCase

from news.models import Comment, News
from users.models import Position, User, UserRole


class NewsModelTest(TestCase):
    """
    Тестирование модели News.
    """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            email='test@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            reward_points=0,
            is_staff=True,
            is_active=True,
        )
        News.objects.create(news_author=user, news_title='Test news')

    def test_field_labels(self):
        news = News.objects.get(id=1)
        labels = {
            'news_title': 'Заголовок новости',
            'news_image': 'Картинка новости',
            'news_date': 'Дата публикации новости',
        }
        for field, label in labels.items():
            with self.subTest(field=field):
                field_label = news._meta.get_field(field).verbose_name
                self.assertEqual(field_label, label)

    def test_image_field_blank(self):
        news = News.objects.get(id=1)
        image = news.news_image
        self.assertEqual(image, '')


class CommentModelTest(TestCase):
    """
    Тестирование модели Comment.
    """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            email='test@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            reward_points=0,
            is_staff=True,
            is_active=True,
        )
        news = News.objects.create(
            news_author=user, news_title='Test news', news_text='Text news'
        )
        Comment.objects.create(
            news=news, comment_text='Test comment', comment_author=user
        )

    def test_field_labels(self):
        comments = Comment.objects.get(id=1)
        labels = {
            'news': 'Новость',
            'comment_text': 'Текст комментария',
            'comment_author': 'Автор комментария',
            'comment_date': 'Дата комментария',
        }
        for field, label in labels.items():
            with self.subTest(field=field):
                field_label = comments._meta.get_field(field).verbose_name
                self.assertEqual(field_label, label)

    def test_create_comment(self):
        comment = Comment.objects.get(id=1)
        news = News.objects.get(id=1)
        user = User.objects.get(id=1)
        self.assertEqual(comment.comment_text, 'Test comment')
        self.assertEqual(comment.news, news)
        self.assertEqual(comment.comment_author, user)
