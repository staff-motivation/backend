# Generated by Django 3.2.19 on 2023-10-04 11:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0005_alter_task_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[
                    ('created', 'Created'),
                    ('returned_for_revision', 'Returned for revision'),
                    ('sent_for_review', 'Sent for review'),
                    ('approved', 'Approved'),
                ],
                default='created',
                max_length=21,
            ),
        ),
    ]
