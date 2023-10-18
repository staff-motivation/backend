from datetime import date

from dateutil.relativedelta import relativedelta  # type: ignore
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = (
        'Reset monthly reward points for all users and clear user achievements'
    )

    def handle(self, *args, **kwargs):
        today = date.today()
        today.replace(day=1)
        today + relativedelta(day=31)

        # Reset monthly reward points for all users
        User.objects.update(reward_points_for_current_month=0)

        # Clear user achievements
        User.objects.all().prefetch_related('achievements').update(
            achievements=None
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Monthly reward points and user achievements reset complete.'
            )
        )
