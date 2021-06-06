from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # создание нового поста
    path("new/", views.new_post, name="new_post"),
    # страница подписок пользователя
    path("follow/", views.follow_index, name="follow_index"),
    # страница для подписки на автора
    path("<str:username>/follow/", views.profile_follow,
         name="profile_follow"),
    # страница отписаться от автора
    path("<str:username>/unfollow/", views.profile_unfollow,
         name="profile_unfollow"),
    # страница постов группы
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    # страничка пользователя
    path("<str:username>/", views.profile, name="profile"),
    # просмотр поста пользователя
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    # страница редактирования записи
    path("<str:username>/<int:post_id>/edit/",
         views.post_edit, name="post_edit"),
    # страница добавления комментария
    path("<str:username>/<int:post_id>/comment/",
         views.add_comment, name="add_comment"),
]
