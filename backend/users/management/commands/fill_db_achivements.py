from django.core.management.base import BaseCommand

from users.models import Achievement


class Command(BaseCommand):
    help = 'Добавление достижений в базу данных.'

    def handle(self, *args, **kwargs):
        Achievement.objects.get_or_create(
            name='Выполено 10 задач',
            value=20,
            description='Достижение за 10 выполненных задач.')
        Achievement.objects.get_or_create(
            name='Выполено 20 задач',
            value=40,
            description='Достижение за 20 выполненных задач.')
        Achievement.objects.get_or_create(
            name='Соблюдение дедлайна',
            value=30,
            description='Достижение за выполение задач в срок.')

        self.stdout.write(self.style.SUCCESS('Достижения добавлены.'))
