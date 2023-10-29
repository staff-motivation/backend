from datetime import date

from django.core.management.base import BaseCommand

from tasks.models import Task
from users.models import Achievement, User, UserAchievement


class Command(BaseCommand):
    help = 'Выдача достижений всем пользователям с 10 выполненными задачами.'

    def handle(self, *args, **kwargs):
        current_year = date.today().year
        current_month = date.today().month
        all_users = User.objects.all()
        achievement = Achievement.objects.get(name='Выполено 10 задач')
        for user in all_users:
            tasks_count = Task.objects.filter(
                assigned_to=user.id,
                deadline__month=current_month,
                deadline__year=current_year,
                status=Task.APPROVED,
            ).count()
            if tasks_count >= 10:
                _, created = UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement,
                )
                if created:
                    user.reward_points += achievement.value
                    user.reward_points_for_current_month += achievement.value
                    user.save()

        self.stdout.write(
            self.style.SUCCESS('Достижения "Выполено 10 задач" выданы.')
        )
