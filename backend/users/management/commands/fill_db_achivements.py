from django.core.management.base import BaseCommand

from users.models import Achievement


class Command(BaseCommand):
    help = 'Добавление достижений в базу данных.'

    def handle(self, *args, **kwargs):
        Achievement.objects.get_or_create(
            name='Качество работы',
            value=30,
            description='Достижение за 30 выполненных задач в срок.',
        )
        Achievement.objects.get_or_create(
            name='Соблюдение дедлайна',
            value=45,
            description='Достижение за выполение задач в срок.',
        )

        self.stdout.write(self.style.SUCCESS('Достижения добавлены.'))
