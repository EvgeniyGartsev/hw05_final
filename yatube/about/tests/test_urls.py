from django.test import TestCase, Client
from django.urls import reverse


class AboutTest(TestCase):
    '''Проверяет статические страницы about'''
    STATUS_CODE_GET = 200

    def setUp(self):
        self.guest_client = Client()

    def test_pages_for_unautorized_client(self):
        '''Проверяем доступность страниц для неавторизованного клиента'''
        # словарь адрес - код ответа
        address_status_code_name = {
            "/about/author/": self.STATUS_CODE_GET,
            "/about/tech/": self.STATUS_CODE_GET,
        }
        for url, status_code in address_status_code_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_templates_for_unautorized_client(self):
        '''Проверяем шаблоны для неавторизованного клиента'''
        # создаем словарь адрес - название шаблона
        templates_reverse_names = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }

        for template, reverse_name in templates_reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
