from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command


def reset_monthly_reward_points_and_achievements():
    call_command('reset_monthly_reward_points')


def achievement_for_no_delay():
    call_command('achievement_for_no_delay')


scheduler = BackgroundScheduler()
scheduler.add_job(
    reset_monthly_reward_points_and_achievements, 'cron', day='1'
)
scheduler.add_job(achievement_for_no_delay, 'cron', day='last')
scheduler.start()
