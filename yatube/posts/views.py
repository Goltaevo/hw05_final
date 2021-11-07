from django.conf import settings as s
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, s.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.all()
    paginator = Paginator(post_list, s.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    following: bool = False
    # Берем автора профайла
    author = get_object_or_404(User, username=username)
    # Берем список подписавшихся пользователей автора,
    subscriptions = author.following.all()
    # Проверяем, содержат ли подписки автора
    # пользователя, который просматривает его профайл
    for subscription in subscriptions:
        if subscription.user == request.user:
            following = True
    # Формируем вывод список постов автора с разбивкой на страницы
    posts_list = Post.objects.filter(author=author)
    paginator = Paginator(posts_list, s.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = request.user
        form_instance_with_author = form.save(commit=False)
        form_instance_with_author.author = user
        form_instance_with_author.save()
        return redirect('posts:profile', username=user.username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit: bool = False
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None)
    if post.author == user:
        if request.method == 'POST' and form.is_valid():
            post.text = form.cleaned_data['text']
            post.image = form.cleaned_data['image']
            post.save()
            return redirect('posts:post_detail', post_id=post.id)
        form = PostForm(instance=post)
        is_edit: bool = True
        context = {
            'form': form,
            'is_edit': is_edit,
            'post_id': post_id,
        }
        return render(request, template, context)
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    # Берем список подписок нашего пользователя
    subscriptions = Follow.objects.filter(user=request.user)
    posts_list = list()
    # Из списка подписок берём каждую подписку
    for subscription in subscriptions:
        # В каждой подписке берём автора, на которого подписан пользователь
        # у автора берем все его посты
        # для того, чтобы список постов был итерируемым добавляем метод all()
        for post in subscription.author.posts.all():
            posts_list.append(post)
    # Добавляем разбивку на страницы
    paginator = Paginator(posts_list, s.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
            'page_obj': page_obj,
        }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    template = 'posts/became_follow.html'
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, username=username)
    # Проверяем, что пользователь еще не подписан на автора
    if request.user.username != username:
        user_already_subscribed = False
        # Берем у автора все подписки  пользователей
        subscriptions = author.following.all()
        # Проверяем, есть ли в этих подписках наш пользователь
        # просматривающий его профайл
        for subscription in subscriptions:
            if subscription.user == request.user:
                user_already_subscribed = True
        # Если пользователя среди текущих подписок автора не нашли,
        # то создаем подписку
        if not user_already_subscribed:
            Follow.objects.create(user=user, author=author)

    context = {
            'author': author,
        }
    return render(request, template, context)


@login_required
def profile_unfollow(request, username):
    template = 'posts/unfollow.html'
    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=user, author=author).delete()
    context = {
            'author': author,
        }
    return render(request, template, context)
