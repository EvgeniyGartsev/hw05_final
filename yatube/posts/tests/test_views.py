import tempfile
# shutil для работы с файлами, здесь для удаления директории
import shutil
# для поочередного создания постов по времени импортируем time
import time

from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from posts.models import Group, Post, Follow, Comment

User = get_user_model()


class PostPagesTest(TestCase):
    '''Проверка доступности шаблонов и контекста
    который передается в шаблон'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем временный каталог для хранения картинок
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # создаем байт последовательности для имитации картинки
        # из двух пикселей
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        small_gif_two = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        uploaded_two = SimpleUploadedFile(
            name='small_two.gif',
            content=small_gif_two,
            content_type='image/gif'
        )
        # создаем записи в БД
        cls.group_one = Group.objects.create(
            title="group_one",
            slug="groupone",
            description="This is first group"
        )
        cls.group_two = Group.objects.create(
            title="group_two",
            slug="grouptwo",
            description="This is second group"
        )
        cls.user = User.objects.create_user(username="alex")
        cls.user_two = User.objects.create_user(username="KillBill")
        cls.user_three = User.objects.create_user(username="JohnTravolta")
        cls.post_one = Post.objects.create(
            id=1,
            text="a" * 20,
            author=cls.user,
            group=cls.group_one,
            image=uploaded,
        )
        # создаем второй пост, спустя секунду после первого
        # чтобы обеспечить различие дат создания поста
        time.sleep(0.1)
        cls.post_two = Post.objects.create(
            id=2,
            text="b" * 20,
            author=cls.user,
            group=cls.group_two,
            image=uploaded_two,
        )

    @classmethod
    def tearDownClass(cls):
        # удаляем директорию после тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # создаем неавторизированного клиента
        self.guest_client = Client()
        # получаем из БД зарегистрированного пользователя
        self.user = User.objects.get(username=self.user)
        self.user_two = User.objects.get(username=self.user_two)
        self.user_three = User.objects.get(username=self.user_three)
        # создаем клиента
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        self.authorized_client_three = Client()
        # авторизируем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_two.force_login(self.user_two)
        self.authorized_client_three.force_login(self.user_three)

    def test_templates_for_unautorized_client(self):
        '''Проверяем шаблоны для неавторизованного клиента'''
        # создаем словарь адрес - название шаблона
        templates_reverse_names = {
            "index.html": reverse("index"),
            "group.html": reverse("group_posts",
                                  kwargs={"slug": self.group_one.slug}),
        }

        for template, reverse_name in templates_reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_templates_for_autorized_client(self):
        '''Проверка шаблонов для авторизованного клиента'''
        # создаем словарь адрес - название шаблона
        templates_reverse_names = {
            "index.html": reverse("index"),
            "group.html": reverse("group_posts",
                                  kwargs={"slug": self.group_one.slug}),
            "post_new_edit.html": reverse("new_post"),
        }

        for template, reverse_name in templates_reverse_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_context(self):
        '''Проверка контекста для index'''
        response = self.guest_client.get(reverse("index"))
        # проверяем что первый элемент на страницы
        # соответствует ожидаемому, т.к. создали
        # два поста, то проверяем что первый на странице -
        # соответствует последнему созданному по дате
        first_object = response.context["page"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, self.post_two.text)
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_image_0, self.post_two.image)

    def test_group_page_context(self):
        '''Проверка контекста для группы'''
        response = self.guest_client.get(reverse("group_posts",
                                         kwargs={"slug": self.group_one.slug}))
        # проверяем что первый элемент на страницы
        # соответствует ожидаемому
        first_object_post = response.context["page"][0]
        post_group = response.context["group"].slug
        post_text_0 = first_object_post.text
        post_author_0 = first_object_post.author.username
        post_image_0 = first_object_post.image
        self.assertEqual(post_text_0, self.post_one.text)
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_group, self.group_one.slug)
        self.assertEqual(post_image_0, self.post_one.image)

    def test_new_page_context(self):
        '''Проверка контекста для страницы создания поста'''
        response = self.authorized_client.get(reverse("new_post"))
        # словарь ожидаемых типов полей
        form_fields = {
            "text": forms.CharField,
            "group": forms.ModelChoiceField,
        }
        # Проверяем, что типы полей формы в словаре
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_page_context(self):
        '''Проверка контекста страницы редактирования поста
        проверяем что в форму попали нужные данные из БД'''
        response = self.authorized_client.get(reverse("post_edit",
                                              kwargs={
                                                  "username": self.user,
                                                  "post_id": self.post_one.id
                                              }))
        # получаем форму из страницы
        form = response.context["form"].initial
        # из формы получаем данные
        text_form = form["text"]
        group_form = form["group"]
        # получаем данные из БД
        text_from_db = self.post_one.text
        group_from_db = Group.objects.get(group__id=1)
        self.assertEqual(text_form, text_from_db)
        self.assertEqual(group_form, group_from_db.id)

    def test_profile_page_context(self):
        '''Проверка контекста для страницы профиля пользователя'''
        response = self.authorized_client.get(reverse("profile",
                                              kwargs={"username": self.user}))
        # проверяем что первый элемент на страницы
        # соответствует ожидаемому
        first_object_post = response.context["page"][0]
        posts_count_on_page = response.context["posts_count"]
        posts_count_on_db = Post.objects.count()
        author_name_on_page = response.context["author_name"].username
        author_name_on_db = User.objects.get(posts__id=2).username
        post_text_0 = first_object_post.text
        post_image_0 = first_object_post.image
        # проверяем переменную кол-ва постов
        self.assertEqual(posts_count_on_page, posts_count_on_db)
        # проверяем автора
        self.assertEqual(author_name_on_page, author_name_on_db)
        self.assertEqual(post_text_0, self.post_two.text)
        self.assertEqual(post_image_0, self.post_two.image)

    def test_post_page_context(self):
        '''Проверка контекста для страницы поста'''
        response = self.authorized_client.get(reverse("post",
                                              kwargs={
                                                  "username": self.user,
                                                  "post_id": self.post_two.id,
                                              }))
        # проверяем что первый элемент на страницы
        # соответствует ожидаемому
        first_object_post = response.context["post"]
        posts_count_on_page = response.context["posts_count"]
        posts_count_on_db = Post.objects.count()
        author_name_on_page = response.context["author_name"].username
        author_name_on_db = User.objects.get(posts__id=2).username
        post_text_0 = first_object_post.text
        post_image_0 = first_object_post.image
        # проверяем переменную кол-ва постов
        self.assertEqual(posts_count_on_page, posts_count_on_db)
        # проверяем автора
        self.assertEqual(author_name_on_page, author_name_on_db)
        self.assertEqual(post_text_0, self.post_two.text)
        self.assertEqual(post_image_0, self.post_two.image)

    def test_post_not_included_in_group(self):
        '''Проверяем что пост не попал в группу,
        для которой он не предназначен'''
        response = self.guest_client.get(reverse("group_posts",
                                         kwargs={"slug": self.group_two.slug}))
        first_object_post = response.context["page"][0]
        post_group = response.context["group"].slug
        post_text_0 = first_object_post.text
        self.assertNotEqual(post_text_0, self.post_one.text)
        self.assertNotEqual(post_group, self.group_one.slug)

    def test_cache_index_page(self):
        '''Проверка кэширования на 20 секунд главной страницы'''
        # получаю страницу до добавления поста
        response_before = self.guest_client.get(reverse("index"))
        # создаю пост
        self.post_three = Post.objects.create(
            id=3,
            text="b" * 20,
            author=self.user,
            group=self.group_two
        )
        # получаю страницу после добавления поста
        response_after_add_post = self.guest_client.get(reverse("index"))
        # сравниваю страницы до и после добавления, должны быть одинаковыe
        self.assertEqual(response_before.content,
                         response_after_add_post.content)
        # очищаем кэш
        cache.clear()
        response_after_clear_cache = self.guest_client.get(reverse("index"))
        # снова сравниваем страницы, должны быть разные
        self.assertNotEqual(response_before.content,
                            response_after_clear_cache.content)

    def test_follow(self):
        '''Проверяем, что авторизованный пользователь
        может подписываться на пользователей и удалять подписку'''
        # получаем кол-во записей в подписках
        count_follow = Follow.objects.all().count()
        # подписываемся на автора
        self.authorized_client_two.get(reverse("profile_follow",
                                       kwargs={
                                               "username": self.user
                                               }))
        # проверяем кол-во записей в подписках
        self.assertEqual(Follow.objects.all().count(), count_follow + 1)
        # отписываемся от автора
        self.authorized_client_two.get(reverse("profile_unfollow",
                                       kwargs={
                                               "username": self.user
                                               }))
        # проверяем кол-во записей в подписках
        self.assertEqual(Follow.objects.all().count(), count_follow)

    def test_follow_index(self):
        '''Проверяем что в ленте пользователя появляются посты
        автора, на которого он подписан и не появляются в ленте
        пользователя, который не подписан'''
        # подписанный пользователь
        self.authorized_client_two.get(reverse("profile_follow",
                                       kwargs={
                                               "username": self.user
                                               }))
        # получаем страницу подписанного пользователя
        response_follower = (self.authorized_client_two.get(
                             reverse("follow_index")))
        # получаем страницу неподписанного пользователя
        response_unfollower = (self.authorized_client_three.get(
                               reverse("follow_index")))
        # проверяем что посты автора есть у подписанного пользователя
        # и нет у неподписанного
        self.assertEqual(len(response_follower.context["page"]),
                         len(response_unfollower.context["page"]) + 2)

    def test_add_comment(self):
        '''Проверяем что авторизованный пользователь может
        комментировать посты, а неавторизованный не может'''
        # получаем кол-во комментариев
        count_comment = Comment.objects.all().count()
        # данные для пост запроса
        form_data = {"post": self.post_one.id,
                     "author": self.user,
                     "text": "This is great post"}
        # оставляем коммент авторизированным пользователем
        self.authorized_client_two.post(reverse("add_comment",
                                        kwargs={
                                            "username": self.user,
                                            "post_id": 1
                                        }), data=form_data, follow=True)
        # проверяем что коммент добавился
        self.assertEqual(Comment.objects.all().count(), count_comment + 1)
        # оставляем коммент неавторизированным пользователем
        self.guest_client.post(reverse("add_comment",
                               kwargs={
                                       "username": self.user,
                                       "post_id": 1
                                       }), data=form_data, follow=True)
        # проверяем что кол-во комментов не изменилось
        self.assertEqual(Comment.objects.all().count(), count_comment + 1)


class PaginatorTest(TestCase):
    '''Проверка пагинатора'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем 15 записей, чтобы проверить
        # пагинатор выводит по 10 на страницу
        cls.group = Group.objects.create(
            title="group_one",
            slug="groupone",
            description="This is first group"
        )
        cls.user = User.objects.create_user(username="alex")
        for i in range(15):
            cls.post = Post.objects.create(
                text="a" * 20,
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        # создаем неавторизированного клиента
        self.guest_client = Client()
        # получаем из БД зарегистрированного пользователя
        self.user = User.objects.get(username=self.user)
        # создаем клиента
        self.authorized_client = Client()
        # авторизируем пользователя
        self.authorized_client.force_login(self.user)

    def test_number_posts_on_first_page_index(self):
        '''Проверяем кол-во постов на первой странице'''
        response = self.guest_client.get(reverse("index"))
        # проверяем что на первой страницы выводится 10 постов
        self.assertEqual(len(response.context["page"]), 10)

    def test_number_posts_on_second_page_index(self):
        '''Проверяем кол-во постов на второй странице'''
        response = self.guest_client.get(reverse("index") + "?page=2")
        # проверяем что на второй страницы выводится 5 постов
        self.assertEqual(len(response.context["page"]), 5)
