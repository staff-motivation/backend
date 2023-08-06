# Generated by Django 3.2.19 on 2023-08-06 15:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20230806_1319'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Backend', 'Backend'), ('Frontend', 'Frontend'), ('UX_UI', 'Ux Ui'), ('QA', 'Qa'), ('None', 'None')], default='None', max_length=10, verbose_name='Подразделение')),
                ('description', models.TextField(help_text='Добавьте описание подразделения', verbose_name='Описание')),
                ('image', models.ImageField(blank=True, help_text='Загрузите изображение', upload_to='users/department/%Y/%m/%d', verbose_name='Изображение')),
            ],
            options={
                'verbose_name': 'Подразделение',
                'verbose_name_plural': 'Подразделения',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_department', to='users.department', verbose_name='Подразделение'),
        ),
    ]
