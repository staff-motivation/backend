# Generated by Django 3.2.19 on 2023-10-14 16:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('department', '0002_alter_department_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='description',
            field=models.TextField(
                blank=True,
                help_text='Добавьте описание подразделения',
                verbose_name='Описание',
            ),
        ),
    ]
