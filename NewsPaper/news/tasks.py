from celery import shared_task
from django.core.mail import send_mail
from .models import Post, Subscriber
from django.utils import timezone

@shared_task
def send_notification_to_subscribers(news_id):
    try:
        news = Post.objects.get(pk=news_id)
        subscribers = Subscriber.objects.all()  # Получаем всех подписчиков
        if subscribers:
            subject = "New post is released"
            message = f"New news/article is published: {news.title}. Look at the website."
            sender_email = "arseniykaragodin@yandex.com"  #  email сервера
            recipient_list = [subscriber.email for subscriber in subscribers]
            send_mail(subject, message, sender_email, recipient_list)
    except Post.DoesNotExist:
        pass


@shared_task
def send_weekly_newsletter():
    # Получение последних новостей (например, за последнюю неделю)
    last_week = timezone.now() - timezone.timedelta(weeks=1)
    latest_news = Post.objects.filter(created_at__gte=last_week, post_type='news')

    # Получение списка всех подписчиков
    subscribers = Subscriber.objects.all()

    if subscribers:
        subject = 'Weekly Newsletter'

        for subscriber in subscribers:
            recipient = subscriber.email
            message = 'Here are the latest news from our website:\n\n'

            for news in latest_news:
                message += f"{news.title}\n{news.text}\n\n"

            send_mail(subject, message, 'arseniykaragodin@yandex.com', [recipient])
