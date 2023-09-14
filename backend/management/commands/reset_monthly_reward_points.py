from django.core.management.base import BaseCommand
from datetime import date
from dateutil.relativedelta import relativedelta
from users.models import User


class Command(BaseCommand):
    help = 'Reset monthly reward points for all users'
    def handle(self, *args, **kwargs):
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today + relativedelta(day=31)
        User.objects.update(reward_points_for_current_month=0)
        self.stdout.write(self.style.SUCCESS('Monthly reward points reset complete.'))