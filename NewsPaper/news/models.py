from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # Суммарный рейтинг каждой статьи автора умножается на 3
        post_rating = sum(post.rating for post in self.post_set.all()) * 3

        # Суммарный рейтинг всех комментариев автора
        comment_rating = sum(comment.rating for comment in Comment.objects.filter(post__author=self))

        # Суммарный рейтинг всех комментариев к статьям автора
        post_comment_rating = sum(comment.rating for comment in Comment.objects.filter(post__author=self))

        # Обновляем рейтинг автора
        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    ARTICLE = 'article'
    NEWS = 'news'
    POST_CHOICES = [
        (ARTICLE, 'Article'),
        (NEWS, 'News'),
    ]

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        preview_length = 124
        if len(self.text) <= preview_length:
            return self.text
        else:
            return self.text[:preview_length].strip() + '...'

    #To save news/articles in create I added settings.AUTH_USER_MODEL here:
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    post_type = models.CharField(max_length=7, choices=POST_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
