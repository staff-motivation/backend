# Generated by Django 3.2.19 on 2023-09-12 18:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='news_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='news', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_author',
            field=models.ForeignKey(db_column='comment_author', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария'),
        ),
        migrations.AddField(
            model_name='comment',
            name='news',
            field=models.ForeignKey(db_column='news', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='news.news', verbose_name='Новость'),
        ),
    ]