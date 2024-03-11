from django.urls import path
# Импортируем созданное нами представление
from .views import (PostsList, PostDetail, search_news,
                    EditPostView,
                    CreateNewsView, CreateArticleView, DeletePostView
                    )


urlpatterns = [

   # path — означает путь.
   # В данном случае путь ко всем post у нас останется пустым,
   # чуть позже станет ясно почему.
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', PostsList.as_view(), name='post_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
   path('search/', search_news, name='search_news'),
    path('create_news/', CreateNewsView.as_view(), name='create_news'),
    path('create_article/', CreateArticleView.as_view(), name='create_article'),
    path('<int:pk>/edit/', EditPostView.as_view(), name='edit_news'),
    path('edit_article/<int:pk>/', EditPostView.as_view(), name='edit_article'),
   path('<int:pk>/delete/', DeletePostView.as_view(), name='delete_news'),
   path('delete_article/<int:pk>/', DeletePostView.as_view(), name='delete_article'),

]

