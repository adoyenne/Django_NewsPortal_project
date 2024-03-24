from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.urls import reverse

from .models import Post, Category, Subscriber, User

# Сигнал для создания объекта Subscriber при создании нового пользователя
@receiver(post_save, sender=User)
def create_subscriber(sender, instance, created, **kwargs):
    if created:
        Subscriber.objects.create(user=instance, email=instance.email)

# Сигнал для отправки уведомлений подписчикам при добавлении поста в категорию
@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(sender, instance, action, **kwargs):
    if action == 'post_add':
        subject = f'New {instance.get_post_type_display()} in categories: {", ".join(instance.categories.values_list("name", flat=True))}'
        text_content = f'Post: {instance.title}\n\n{instance.text}\n\nPost link: http://127.0.0.1:8000{reverse("post_detail", args=[instance.pk])}'
        html_content = f'<p>Post: {instance.title}</p><p>{instance.text}</p><p><a href="http://127.0.0.1:8000{reverse("post_detail", args=[instance.pk])}">Post link</a></p>'

        subscribers_emails = Subscriber.objects.filter(subscribed_categories__in=instance.categories.all()).values_list('email', flat=True)

        for email in subscribers_emails:
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()