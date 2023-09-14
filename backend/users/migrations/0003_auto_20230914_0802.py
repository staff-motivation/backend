# Generated by Django 3.2.19 on 2023-09-14 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_hardskill_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reward_points_for_current_month',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='experience',
            field=models.IntegerField(default=1, verbose_name='Рабочий стаж в команде'),
        ),
    ]
