# Generated by Django 3.2.19 on 2023-10-25 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0007_task_department'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-created_at'], 'verbose_name': 'Задачу', 'verbose_name_plural': 'Задачи'},
        ),
    ]