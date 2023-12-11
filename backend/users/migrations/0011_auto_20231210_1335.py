# Generated by Django 3.2.22 on 2023-12-10 08:35

import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20231109_2139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='contacts',
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.DeleteModel(
            name='UserContact',
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False,
                                           verbose_name='ID')),
                ('phone',
                 models.CharField(blank=True, max_length=20, null=True,
                                  verbose_name='Номер телефона')),
                ('telegram',
                 models.CharField(blank=True, max_length=255, null=True,
                                  verbose_name='Аккаунт telegram')),
                ('github',
                 models.CharField(blank=True, max_length=255, null=True,
                                  verbose_name='Аккаунт github')),
                ('linkedin',
                 models.CharField(blank=True, max_length=255, null=True,
                                  verbose_name='Аккаунт linkedin')),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='contacts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Контакт',
                'verbose_name_plural': 'Контакты',
            },
        ),
    ]
