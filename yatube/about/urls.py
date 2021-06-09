from django.urls import path

from . import views

# определяем пространство имен
app_name = "about"

urlpatterns = [
    # страница об авторе, генерируется специальным view
    # классом для статичных страниц
    path("author/", views.AuthorStaticPage.as_view(), name="author"),
    path("tech/", views.TechnologyStaticPage.as_view(), name="tech"),
]
