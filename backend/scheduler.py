from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def reset_monthly_reward_points():
    call_command('reset_monthly_reward_points')

scheduler = BackgroundScheduler()
scheduler.add_job(reset_monthly_reward_points, 'cron', day='1')
scheduler.start()