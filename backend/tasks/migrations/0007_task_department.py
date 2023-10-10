# Generated by Django 3.2.19 on 2023-10-10 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0001_initial'),
        ('tasks', '0006_alter_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_tasks', to='department.department'),
        ),
    ]
