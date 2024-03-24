from django.shortcuts import render, get_object_or_404, redirect
# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Post, Category, Subscriber
from .forms import NewsForm, ArticleForm
from django.http import Http404
from .forms import NewsForm, ArticleForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import models
from django.shortcuts import get_object_or_404

class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    #ordering = 'name'
    #queryset = Product.objects.filter(price__lt = 170)
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'posts.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'Posts'

    paginate_by = 2 # вот так мы можем указать количество записей на странице

    # Метод для получения queryset объектов Post, отсортированных по дате публикации:
    def get_queryset(self):
        # Получаем все объекты Post, отсортированные по дате публикации
        # Get all objects sorted by creation date
        return Post.objects.order_by('-created_at')


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — post.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'



def search_news(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    date = request.GET.get('date')

    paginate_by = 2

    search_results = Post.objects.all()
    categories = Category.objects.all()

    if query:
        search_results = search_results.filter(Q(title__icontains=query) | Q(text__icontains=query))

    if category:
        search_results = search_results.filter(categories__name=category)

    if date:
        search_results = search_results.filter(created_at__gte=date)

    paginator = Paginator(search_results, paginate_by)
    page = request.GET.get('page')

    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        search_results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        search_results = paginator.page(paginator.num_pages)

    context = {
        'query': query,
        'category_id': category,
        'categories': categories,
        'date': date,
        'search_results': search_results
    }
    return render(request, 'search_news.html', context)

class CreateNewsView(PermissionRequiredMixin,CreateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = NewsForm
    template_name = 'create_news.html'

    def form_valid(self, form):
        news = form.save(commit=False)
        news.post_type = 'news'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_list')

class CreateArticleView(PermissionRequiredMixin,CreateView):
    permission_required = ('news.add_post',)
    model = Post
    form_class = ArticleForm
    template_name = 'create_article.html'

    def form_valid(self, form):
        article = form.save(commit=False)
        article.post_type = 'article'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_list')



class EditPostView(PermissionRequiredMixin,UpdateView):
    permission_required = ('news.change_post',)

    model = Post
    fields = ['title', 'text', 'categories']

    def get_template_names(self):
        post = self.get_object()
        if post.post_type == 'article':

            return ['edit_article.html']
        elif post.post_type == 'news':
            return ['edit_news.html']
        else:

            pass
    # Overriding get_context_data to provide form to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    # Overriding form_valid to save changes and redirect after successful editing
    def form_valid(self, form):
        post = form.save(commit=False)
        # Save the changes
        post.save()
        return redirect('/')  # Redirect after successful editing

    # Overriding get to set the post_type attribute
    def get(self, request, *args, **kwargs):
        self.post_type = self.kwargs.get('post_type', None)
        return super().get(request, *args, **kwargs)

    # Overriding post to set the post_type attribute
    def post(self, request, *args, **kwargs):
        self.post_type = self.kwargs.get('post_type', None)
        return super().post(request, *args, **kwargs)


class DeletePostView(PermissionRequiredMixin,DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    success_url = reverse_lazy('post_list')  # This redirects to the home page after deleting a post

    def get_template_names(self):
        post = self.get_object()
        if post.post_type == 'article':

            return ['delete_article.html']
        elif post.post_type == 'news':
            return ['delete_news.html']
        else:
            pass

    def delete(self, request, *args, **kwargs):
        """
        Overridden method to perform the deletion of the post.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


#######################################################################

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        # Получаем категорию из запроса, обрабатываемая или вызываем ошибку 404, если категория не существует
        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)

        # Получаем текущего пользователя
        user = request.user

        # Получаем объект подписчика для текущего пользователя, создаем его, если он не существует
        subscriber, created = Subscriber.objects.get_or_create(user=user, email=user.email)

        # Обрабатываем действие (подписка или отписка)
        action = request.POST.get('action')
        if action == 'subscribe':
            subscriber.subscribed_categories.add(category)
        elif action == 'unsubscribe':
            subscriber.subscribed_categories.remove(category)

        return redirect('subscriptions')

    # Получаем все категории с аннотацией о том, подписан ли пользователь на них
    categories_with_subscriptions = Category.objects.all().annotate(
        user_subscribed=models.Exists(
            Subscriber.objects.filter(
                user=request.user,
                subscribed_categories=models.OuterRef('pk'),
            )
        )
    ).order_by('name')

    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )

