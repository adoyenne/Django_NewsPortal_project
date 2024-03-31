#Important:
#to run celery simple task like notificatino without scheduled time, use this command: celery -A NewsPaper worker -l INFO
#to run celery scheduled submission, use this command:
# celery -A NewsPaper beat вместе с celery -A NewsPaper worker -l INFO (в разных терминалах)

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


# Определение расписания для задачи рассылки новостей
app.conf.beat_schedule = {
    'send-weekly-newsletter': {
        'task': 'news.tasks.send_weekly_newsletter',  # Путь к задаче
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Каждый понедельник в 8:00
        #'schedule': crontab(hour=15, minute=55, day_of_week=0),  # test
    },
}