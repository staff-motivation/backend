from datetime import date

from django.core.management.base import BaseCommand

from tasks.models import Task
from users.models import Achievement, User, UserAchievement


class Command(BaseCommand):
    help = 'Выдача достижений всем пользователям без просроченных заданий.'

    def handle(self, *args, **kwargs):
        current_year = date.today().year
        current_month = date.today().month
        all_users = User.objects.filter(
            assigned_tasks__is_overdue=False,
            assigned_tasks__deadline__month=current_month,
            assigned_tasks__deadline__year=current_year,
            assigned_tasks__status=Task.APPROVED,
        ).distinct()
        achievement = Achievement.objects.get(name='Соблюдение дедлайна')
        for user in all_users:
            UserAchievement.objects.create(user=user, achievement=achievement)
            user.reward_points += achievement.value
            user.reward_points_for_current_month += achievement.value
            user.save()

        self.stdout.write(
            self.style.SUCCESS('Достижения "Соблюдение дедайна" выданы.')
        )
