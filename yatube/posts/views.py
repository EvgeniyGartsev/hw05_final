from django.shortcuts import (get_list_or_404,
                              redirect, render,
                              get_object_or_404)
# paginator для вывода определенного кол-ва постов на страницу
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
# login_required редиректит на страницу settings.LOGIN_URL
from django.contrib.auth.decorators import login_required
# reverse для перенаправления на страницу по имени
from django.urls import reverse

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from yatube.settings import POST_NUMBER


def index(request):
    '''Show last posts'''
    posts = Post.objects.all()
    paginator = Paginator(posts, POST_NUMBER)
    # из url извлекаем номер запрошенной страницы
    page_number = request.GET.get("page")
    # получем записи для запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    '''Show posts group'''
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group__slug=slug)
    paginator = Paginator(posts, POST_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


def profile(request, username):
    '''Show user page'''
    author_name = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author__username=username)
    paginator = Paginator(user_posts, POST_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # отображение кнопки подписаться если не подписан
    is_followed = False
    if request.user.is_authenticated:
        is_followed = Follow.objects.filter(user=request.user,
                                            author__username=username).exists()
    # не показываем автору кнопку подписки
    is_author = author_name.username == request.user
    # получаем кол-во подписчиков пользователя
    follower_count = Follow.objects.filter(author__username=username).count()
    # получаю количество авторов, на которых подписан пользователь
    following_count = Follow.objects.filter(user__username=username).count()
    return render(request, "profile.html",
                  {"page": page,
                   "posts_count": user_posts.count(),
                   "author_name": author_name,
                   "is_followed": is_followed,
                   "is_author": is_author,
                   "follower_count": follower_count,
                   "following_count": following_count,
                   })


def post_view(request, username, post_id):
    '''Show one user post'''
    author_name = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    posts_count = Post.objects.filter(author__username=username).count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post__id=post_id)
    # получаем кол-во подписчиков пользователя
    follower_count = Follow.objects.filter(author__username=username).count()
    # получаю количество авторов, на которых подписан пользователь
    following_count = Follow.objects.filter(user__username=username).count()
    # отображение кнопки подписаться если не подписан
    is_followed = False
    if request.user.is_authenticated:
        is_followed = Follow.objects.filter(user=request.user,
                                            author__username=username).exists()
    return render(request, "post_view.html",
                  {"post": post,
                   "posts_count": posts_count,
                   "author_name": author_name,
                   "form": form,
                   "comments": comments,
                   "is_followed": is_followed,
                   "follower_count": follower_count,
                   "following_count": following_count,
                   })


@login_required(login_url="login")
def new_post(request):
    '''Add new posts'''
    form = PostForm(request.POST or None, files=request.FILES or None)
    # показ кнопок редактировать/добавить пост
    is_edit_post = False
    if form.is_valid():
        print(form.cleaned_data)
        post = Post(text=form.cleaned_data["text"],
                    author=request.user,
                    group=form.cleaned_data["group"],
                    image=form.cleaned_data["image"],)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "post_new_edit.html",
                  {"form": form, "is_edit_post": is_edit_post})


@login_required(login_url="login")
def post_edit(request, username, post_id):
    '''Edit post'''
    post_for_edit = get_object_or_404(Post,
                                      author__username=username,
                                      id=post_id)
    author_name = get_object_or_404(User, posts__id=post_id)
    # проверяем является ли пользователь автором
    is_author = (str(author_name) == request.user.username)
    if not is_author:
        return HttpResponseRedirect(reverse("post",
                                    args=[author_name, post_id]))
    # показ кнопок редактировать/добавить пост
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_for_edit)
    is_edit_post = True
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("post",
                                        args=[username, post_id]))
        return render(request, "post_new_edit.html",
                      {"form": form, "is_edit_post": is_edit_post})
    return render(request, "post_new_edit.html",
                  {"form": form, "post": post_for_edit,
                   "is_edit_post": is_edit_post})


@login_required(login_url="login")
def add_comment(request, username, post_id):
    '''Save comments for posts'''
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid:
            # сохраняем в БД что есть, игнорируя Null
            record = form.save(commit=False)
            record.post = get_object_or_404(Post, id=post_id)
            record.author = get_object_or_404(User, username=request.user)
            record.save()
        return redirect("post", username=username, post_id=post_id)


@login_required(login_url="login")
def follow_index(request):
    '''Вывод постов тех авторов, на которых подписан пользователь'''
    # получаем все посты авторов, на которых подписан пользователь
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, POST_NUMBER)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required(login_url="login")
def profile_follow(request, username):
    '''Подписка на автора'''
    # проверяем что можно подписаться на автора один раз
    author = get_object_or_404(User, username=username)
    is_followed = Follow.objects.filter(user=request.user,
                                        author__username=username).exists()
    # пользователь не может подписаться на самого себя
    if request.user.username != username and not is_followed:
        Follow(user=request.user,
               author=author).save()
    return redirect("profile", username=username)


@login_required(login_url="login")
def profile_unfollow(request, username):
    '''Удаление подписки на автора'''
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author)
    follow.delete()
    return redirect("profile", username=username)


def groups(request):
    '''Show groups'''
    groups = get_list_or_404(Group)
    print(groups)
    paginator = Paginator(groups, POST_NUMBER)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "groups.html", {"page": page})


def page_not_found(request, exception=None):
    '''Handles the error 404'''
    # exception содержит отладочную информацию
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    '''Handles the error 500'''
    return render(request, "misc/500.html", status=500)
