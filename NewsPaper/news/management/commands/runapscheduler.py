import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.management.base import BaseCommand
from news.models import Post, Subscriber
from django.urls import reverse

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_article_list,
            #trigger=CronTrigger(day_of_week='fri', hour='18', minute='00'),  # Каждую пятницу в 18:00
            trigger=CronTrigger(minute="*/2"),  # Запустить каждые 2 минуты (для проверки работы)
            id='send_article_list',
            replace_existing=True,
        )


        logger.info("Added job 'send_article_list'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

def send_article_list():
    # Находим дату последней рассылки
    last_execution = DjangoJobExecution.objects.filter(job_id='send_article_list').order_by('-run_time').first()
    if last_execution:
        last_execution_time = last_execution.run_time
    else:
        # Если это первая рассылка, отправляем все статьи
        last_execution_time = timezone.make_aware(datetime.datetime.min, timezone.get_current_timezone())

    # Фильтруем статьи, опубликованные после последней рассылки
    new_articles = Post.objects.filter(created_at__gt=last_execution_time)

    if new_articles.exists():
        # Получаем список адресов электронной почты подписчиков из базы данных
        recipients = Subscriber.objects.values_list('email', flat=True)

        for article in new_articles:
            # Создаем сообщение для отправки
            subject = 'New article has been published'
            html_content = f'<p>Post: {article.title}</p><p>{article.text}</p><p><a href="http://127.0.0.1:8000{reverse("post_detail", args=[article.pk])}">Post link</a></p>'

            # Отправляем сообщение по списку подписчиков
            msg = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, recipients)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        # Обновляем время выполнения для этой задачи
        last_execution.run_time = timezone.now()
        last_execution.save()