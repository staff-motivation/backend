# Generated by Django 3.2.19 on 2023-08-31 08:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={},
        ),
        migrations.RemoveField(
            model_name='task',
            name='assignees',
        ),
        migrations.RemoveField(
            model_name='task',
            name='creation_date',
        ),
        migrations.RemoveField(
            model_name='task',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='task',
            name='start_date',
        ),
        migrations.AddField(
            model_name='task',
            name='assigned_to',
            field=models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='reward_points',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='team_leader',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_created', to='users.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('created', 'Задача создана'), ('in_progress', 'В процессе выполнения'), ('sent_for_review', 'Отправлена на проверку'), ('completed', 'Принята и выполнена'), ('returned_for_revision', 'Возвращена на доработку')], max_length=21),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.CreateModel(
            name='TaskUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_text', models.TextField()),
                ('status', models.CharField(choices=[('created', 'Задача создана'), ('in_progress', 'В процессе выполнения'), ('sent_for_review', 'Отправлена на проверку'), ('completed', 'Принята и выполнена'), ('returned_for_revision', 'Возвращена на доработку')], max_length=21)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TaskInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
