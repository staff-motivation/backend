# Generated by Django 3.2.19 on 2023-09-12 19:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hardskill',
            name='name',
            field=models.CharField(
                help_text='Введите профессиоанльный навык/хардскилл',
                max_length=255,
                verbose_name='Хардскилл',
            ),
        ),
    ]
