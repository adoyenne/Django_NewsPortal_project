python3 manage.py shell
from news.models import *

#Создаём двух пользователей:

user1 = User.objects.create_user('user1', password='4356')
user2 = User.objects.create_user('user2', password='5332')

user1 = User.objects.get(username='user1')
user2 = User.objects.get(username='user2')

# Создаём объекты Author, связанные с этими пользователями
author1 = Author.objects.create(user=user1, rating=0)
author2 = Author.objects.create(user=user2, rating=0)

# Создаём объекты Category для каждой категории
category1 = Category.objects.create(name='Policy')
category2 = Category.objects.create(name='Sport')
category3 = Category.objects.create(name='Science')
category4 = Category.objects.create(name='Culture')
category5 = Category.objects.create(name='Progress')

#Добавим 2 статьи и 1 новость и присваиваем категории:

# Создаём статьи:
article1 = Post.objects.create(
    author=author1,
    post_type='article',
    title='Djokovic wins Wimbledon again',
    text='Djokovic scores another incredible win at Wimbledon...',
)

article1.categories.add(category2) #присваиваем категорию

article2 = Post.objects.create(
    author=author2,
    post_type='article',
    title='Will Trump win the US presidential election?',
    text=' If the presidential elections in the United States (US) were held today, voters would favour Donald Trump over Joe Biden...',
)

article2.categories.add(category1) #присваиваем категорию

# Создаём новость
news1 = Post.objects.create(
    author=author1,
    post_type='news',
    title='Winners of the Nobel Prize in Physics announced',
    text='Winners of the Nobel Prize in Physics are...',
)
news1.categories.add(category3,category5) #присваиваем две категории\



# Создаём комментарии
comment1 = Comment.objects.create(author=author1, post=article1, user=user1, text='God bless Djokovic')
comment2 = Comment.objects.create(author=author2, post=article2, user=user2, text='Im rooting for Trump, he is a good guy')
comment3 = Comment.objects.create(author=author1, post=news1, user=user1, text='I was waiting this for so long')
comment4 = Comment.objects.create(author=author1, post=article1, user=user2, text='No doubts, Djokovic is a best tennis player')

# Применяем like() и dislike() к объектам
article1.like()
article1.save()

article2.dislike()
article2.save()

news1.like()
news1.save()

comment1.like()
comment1.save()

comment2.dislike()
comment2.save()



# Обновите рейтинги пользователей
author1.update_rating()
author2.update_rating()


# Получаем лучшего пользователя (с наибольшим рейтингом)
best_user = User.objects.all().order_by('-author__rating').first()
best_user.username
best_user.author.rating


# Получаем лучшую статью (с наибольшим рейтингом)
best_post = Post.objects.all().order_by('-rating').first()

if best_post:
    # Выводим информацию о лучшей статье
    print("Date added:", best_post.created_at)
    print("Author:", best_post.author.user.username)
    print("Rating:", best_post.rating)
    print("Title:", best_post.title)
    print("Preview:", best_post.preview())


comments = Comment.objects.filter(post=best_post)


if comments.exists():
    # Выводим информацию о каждом комментарии
    for comment in comments:
        print("Date:", comment.created_at)
        print("User:", comment.user.username)
        print("Rating:", comment.rating)
        print("Text:", comment.text)
        print("------------------------------------------")
else:
    print("No comments found for the best post")
