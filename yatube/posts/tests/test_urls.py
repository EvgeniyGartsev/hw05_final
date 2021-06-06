from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    '''Проверяем доступность страниц'''
    STATUS_CODE_GET = 200
    STATUS_PAGE_NOT_FOUND = 404
    GROUP_TITLE = "group_one"
    GROUP_SLUG = "groupone"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем записи в БД
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
            description="This is first group"
        )
        cls.user = User.objects.create_user(username="alex")
        cls.user_two = User.objects.create_user(username="mixa")
        cls.post = Post.objects.create(
            text="a" * 20,
            author=cls.user,
            id=1
        )

    def setUp(self):
        # создаем неавторизированного клиента
        self.guest_client = Client()
        # получаем из БД зарегистрированного пользователя
        self.user = PostURLTests.user
        # получаем второго пользователя
        self.user_two = PostURLTests.user_two
        # создаем клиента
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        # авторизируем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_two.force_login(self.user_two)

    def test_pages_for_unautorized_client(self):
        '''Проверяем доступность страниц для неавторизованного клиента'''
        # словарь адрес - код ответа
        address_status_code_name = {
            "/": self.STATUS_CODE_GET,
            f"/group/{self.GROUP_SLUG}/": self.STATUS_CODE_GET,
            f"/{self.user.username}/": self.STATUS_CODE_GET,
            f"/{self.user.username}/{self.post.id}/": self.STATUS_CODE_GET,
            # проверка если страница не найдена
            "/page_not_found/": self.STATUS_PAGE_NOT_FOUND,
        }
        for url, status_code in address_status_code_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_pages_for_authorized_author_client(self):
        '''Проверка страниц для авторизованного автора поста'''
        # словарь адрес - код ответа
        address_status_code_name = {
            "/": self.STATUS_CODE_GET,
            f"/group/{self.GROUP_SLUG}/": self.STATUS_CODE_GET,
            f"/{self.user.username}/": self.STATUS_CODE_GET,
            f"/{self.user.username}/{self.post.id}/": self.STATUS_CODE_GET,
            (f"/{self.user.username}/"
             f"{self.post.id}/edit/"): self.STATUS_CODE_GET,
            # проверка если страница не найдена
            "/page_not_found/": self.STATUS_PAGE_NOT_FOUND,
        }
        for url, status_code in address_status_code_name.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_redirect_page_for_unautorized_client(self):
        '''Проверяем редиректы для неавторизированного клиента'''
        # создаем словарь страница - редирект
        urls_redirect_addresses = {
            "/new/": "/auth/login/?next=/new/",
            (f"/{self.user.username}/"
             f"{self.post.id}/edit/"): ("/auth/login/?next="
                                        f"/{self.user.username}/"
                                        f"{self.post.id}/edit/"),
        }
        for url, redirect_address in urls_redirect_addresses.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_redirect_page_for_non_author(self):
        '''Проверяем перенаправление для не автора поста'''
        response = self.authorized_client_two.get((f"/{self.user.username}/"
                                                   f"{self.post.id}/edit/"))
        self.assertRedirects(response, (f"/{self.user.username}/"
                                        f"{self.post.id}/"))


class PostTemplatesTest(TestCase):
    '''Проверяем шаблоны'''
    GROUP_TITLE = "group_one"
    GROUP_SLUG = "groupone"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем записи в БД
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
            description="This is first group"
        )
        cls.user = User.objects.create_user(username="alex")
        cls.post = Post.objects.create(
            text="a" * 20,
            author=cls.user,
            id=1
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username=self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_templates_for_unautorized_client(self):
        '''Проверяем шаблоны для неавторизированного клиента'''
        # создаем словарь адрес - название шаблона
        templates_url_names = {
            "/": "index.html",
            f"/group/{self.GROUP_SLUG}/": "group.html",
            "/auth/login/?next=/new/": "registration/login.html",
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_templates_for_autorized_author_client(self):
        '''Проверка шаблонов для авторизованного автора'''
        # создаем словарь адрес - название шаблона
        templates_url_names = {
            "/": "index.html",
            f"/group/{self.GROUP_SLUG}/": "group.html",
            "/new/": "post_new_edit.html",
            (f"/{self.user.username}/"
             f"{self.post.id}/edit/"): "post_new_edit.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
