from django.shortcuts import (get_list_or_404,
                              redirect, render,
                              get_object_or_404)
# импортируем Paginator для возможности вывода
# определенного количества постов на страницу
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
# login_required - декоратор, который выполняет редирек
# на страницу settings.LOGIN_URL
from django.contrib.auth.decorators import login_required
# reverse для перенаправления на страницу
# по имени пути
from django.urls import reverse

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm

# Количество записей на страницу
POST_NUMBER = 10


def index(request):
    '''Show last posts'''
    # получаем список постов
    posts = get_list_or_404(Post)
    # создаем экземпляр пагинатора, передаем ему
    # данные из БД постов и количество выводимых
    # записей на страницу
    paginator = Paginator(posts, POST_NUMBER)
    # из url извлекаем номер запрошенной страницы
    page_number = request.GET.get("page")
    # получем записи для запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page})


def group_posts(request, slug):
    '''Show posts group'''
    # возвращаем ошибку 404 если группы нет в базе данных
    # если группа есть, то возвращаем объект
    group = get_object_or_404(Group, slug=slug)
    # group__title=group чтобы получить данные из
    # связанной таблицы
    posts = Post.objects.filter(group__slug=slug)
    # создаем экземпляр пагинатора, передаем ему
    # данные из БД постов и количество выводимых
    # записей на страницу
    paginator = Paginator(posts, POST_NUMBER)
    # из url извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получем записи для запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page})


def profile(request, username):
    '''Show user page'''
    # возвращаем ошибку 404 username нет в базе данных
    # если username есть, то возвращаем объект
    author_name = get_object_or_404(User, username=username)
    # получаем все посты автора
    user_posts = Post.objects.filter(author__username=username)
    # создаем экземпляр пагинатора, передаем ему
    # данные из БД постов и количество выводимых
    # записей на страницу
    paginator = Paginator(user_posts, POST_NUMBER)
    # из url извлекаем номер запрошенной страницы
    page_number = request.GET.get('page')
    # получем записи для запрошенной страницы
    page = paginator.get_page(page_number)
    # проверяем подписку текущего пользователя на автора
    # если не подписан, то выводим кнопку подписаться
    following = Follow.objects.filter(
        user=User.objects.get(username=request.user),
        author=User.objects.get(username=username)).exists()
    # проверяем что пользователь не является автором, чтобы
    # не показывать ему кнопку подписки
    is_author = author_name.username == request.user
    return render(request, "profile.html",
                  {"page": page,
                   "posts_count": user_posts.count(),
                   "author_name": author_name,
                   "following": following,
                   "is_author": is_author,
                   })


def post_view(request, username, post_id):
    '''Show one user post'''
    # получаем пост пользователя по id из БД
    # возвращаем ошибку 404 если поста пользователя
    # с таким id нет в базе
    post = get_object_or_404(Post, author__username=username, id=post_id)
    # получаем количество записей пользователя
    posts_count = Post.objects.filter(author__username=username).count()
    # создаем форму для добавления комментария
    form = CommentForm(request.POST or None)
    # достаем комментарии поста
    comments = Comment.objects.filter(post__id=post_id)
    return render(request, "post_view.html",
                  {"post": post,
                   "posts_count": posts_count,
                   "author_name": post.author,
                   "form": form,
                   "comments": comments})


# используем декоратор, если пользователь
# не зарегестрирован, то направляем
# на страницу регистрации
@login_required(login_url="login")
def new_post(request):
    '''Add new posts'''
    # создаем экземпляр формы по данным из
    # post запроса
    form = PostForm(request.POST or None)
    # получаем имя функции для использования в шаблоне
    # для показа кнопок редактировать/добавить пост
    is_edit_post = False
    # если форма прошла валидацию, то
    # отправляем данные в БД
    if form.is_valid():
        # получаем экземпляр Post из БД
        # и передаем ему параметры из формы
        # после валидации через form.cleaned_data
        post = Post(text=form.cleaned_data["text"],
                    author=User.objects.get(
                    username=request.user.get_username()),
                    group=form.cleaned_data["group"])
        # сохраняем данные в БД
        post.save()
        # перенаправляем пользователя на
        # главную страницу
        return HttpResponseRedirect(reverse("index"))
        # если форма не прошла валидацию, открываем ту же форму
    return render(request, "post_new_edit.html",
                  {"form": form, "is_edit_post": is_edit_post})


# не зарегестрирован, то направляем
# на страницу регистрации
@login_required(login_url="login")
def post_edit(request, username, post_id):
    '''Edit post'''
    # получаем пост из БД для редактирования
    post_for_edit = get_object_or_404(Post,
                                      author__username=username,
                                      id=post_id)
    # получаем имя автора поста
    author_name = get_object_or_404(User, posts__id=post_id)
    # проверяем является ли пользователь автором
    is_author = (str(author_name) == request.user.username)
    # если пользователь не является автором поста, то
    # направляем на страницу просмотра поста
    if not is_author:
        return HttpResponseRedirect(reverse("post",
                                    args=[author_name, post_id]))
    # получаем имя функции для использования в шаблоне
    # для показа кнопок редактировать/добавить пост
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post_for_edit)
    is_edit_post = True
    if request.method == "POST":
        # если форма прошла валидацию, то
        # отправляем данные в БД
        if form.is_valid():
            # обновляем данные в БД
            form.save()
            # перенаправляем пользователя на
            # страницу с его постом
            return HttpResponseRedirect(reverse("post",
                                        args=[username, post_id]))
        # если форма не прошла валидацию, открываем ту же форму
        return render(request, "post_new_edit.html",
                      {"form": form, "is_edit_post": is_edit_post})
    return render(request, "post_new_edit.html",
                  {"form": form, "post_id": post_for_edit.id,
                   "is_edit_post": is_edit_post})


@login_required(login_url="login")
def add_comment(request, username, post_id):
    '''Save comments for posts'''
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid:
            # сохраняем в БД что есть, игнорируя Null
            record = form.save(commit=False)
            record.post = Post.objects.get(id=post_id)
            record.author = User.objects.get(username=request.user)
            record.save()
            return redirect("post", username=username, post_id=post_id)


@login_required(login_url="login")
def follow_index(request):
    '''Вывод постов авторов, на которых подписан пользователь'''
    # получаем всех авторов, на которых подписан пользователь
    authors = Follow.objects.filter(user=request.user)
    # получаем все посты авторов, на которые подписан пользователь
    posts = Post.objects.filter(author__following__in=authors)
    paginator = Paginator(posts, POST_NUMBER)
    # из url извлекаем номер запрошенной страницы
    page_number = request.GET.get("page")
    # получем записи для запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    '''Подписка на автора'''
    Follow(user=User.objects.get(username=request.user),
           author=User.objects.get(username=username)).save()
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    '''Удаление подписки на автора'''
    Follow.objects.get(user=User.objects.get(username=request.user),
                       author=User.objects.get(username=username)).delete()
    return redirect("profile", username=username)


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
