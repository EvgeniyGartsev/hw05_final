# импортируем TemplateView для создания статичной страницы
from django.views.generic.base import TemplateView


# view класс для создание статичной страницы об авторе
class AuthorStaticPage(TemplateView):
    '''View class for render static page about author'''
    # обязательный параметр название шаблона
    template_name = "about/author.html"


# view класс для создание статичной страницы о технологиях
class TechnologyStaticPage(TemplateView):
    '''View class for render static page about techologies'''
    # обязательный параметр название шаблона
    template_name = "about/tech.html"
