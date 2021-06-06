from django.urls import path

from . import views

# app_name обязательный параметр
# для того, чтобы работало пространство
# имен namespace для view функции
app_name = "about"

urlpatterns = [
    # страница об авторе, генерируется специальным view
    # классом для статичных страниц
    path("author/", views.AuthorStaticPage.as_view(), name="author"),
    # страница о технологиях, генерируется специальным view
    # классом для статичных страниц
    path("tech/", views.TechnologyStaticPage.as_view(), name="tech"),
]
