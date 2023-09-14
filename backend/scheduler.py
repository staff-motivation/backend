from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

def reset_monthly_reward_points_and_achievements():
    call_command('reset_monthly_reward_points')
    call_command('reset_user_achievements')


scheduler = BackgroundScheduler()
scheduler.add_job(reset_monthly_reward_points_and_achievements, 'cron', day='1')
scheduler.start()
