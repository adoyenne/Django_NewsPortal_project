from django.apps import AppConfig
from django.db.models.signals import m2m_changed

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Импортируем функции сигнала из signals.py
        from . import signals

        # Подключаем функцию к сигналу m2m_changed
        Post = self.get_model('Post')
        m2m_changed.connect(signals.notify_subscribers, sender=Post.categories.through)



