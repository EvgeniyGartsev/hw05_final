import tempfile
# shutil для работы с файлами, здесь для удаления директории
import shutil

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from posts.models import Group, Post

User = get_user_model()


class PostCreateForm(TestCase):
    '''Проверяем форму'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем временный каталог для хранения картинок
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # создаем байт последовательности для имитации картинки
        # из двух пикселей
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # создаем записи в БД
        cls.group_one = Group.objects.create(
            title="group_one",
            slug="groupone",
            description="This is first group"
        )
        cls.user = User.objects.create_user(username="alex")
        cls.user_two = User.objects.create_user(username="bob")
        cls.post_one = Post.objects.create(
            text="a" * 20,
            author=cls.user,
            group=cls.group_one,
            id=1,
        )
        cls.post_two = Post.objects.create(
            text="b" * 20,
            author=cls.user,
            group=cls.group_one,
            id=2,
        )

    @classmethod
    def tearDownClass(cls):
        # удаляем директорию после тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        # получаем из БД зарегистрированного пользователя
        self.user = User.objects.get(username=self.user)
        self.user_two = User.objects.get(username=self.user_two)
        # создаем клиента
        self.authorized_client = Client()
        self.authorized_client_two = Client()
        # авторизируем пользователя
        self.authorized_client.force_login(self.user)
        self.authorized_client_two.force_login(self.user_two)

    def test_create_new_post_in_db(self):
        '''Проверка создания поста в БД'''
        posts_count = Post.objects.count()
        # подготавливаем данные для пост запроса
        form_data = {
            "text": "New post",
            "group": self.group_one.id,
            "image": self.uploaded
        }
        # отправляем post запрос
        response = self.authorized_client.post(reverse("new_post"),
                                               data=form_data,
                                               follow=True)
        # проверяем редирект
        self.assertRedirects(response, reverse("index"))
        # проверяем увеличилось ли кол-во постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # проверяем что наша запись появилась в БД
        self.assertTrue(Post.objects.filter(text=form_data["text"]).exists())

    def test_edit_post(self):
        '''Проверка изменения поста в бд при
        редактировании на странице'''
        form_data = {
            "text": "New text for second post",
            "group": self.group_one.id,
        }
        # изменяем пост из формы
        response = self.authorized_client.post(reverse("post_edit",
                                               kwargs={
                                                   "username": self.user,
                                                   "post_id": self.post_two.id
                                               }),
                                               data=form_data,
                                               follow=True)
        # проверяем редирект
        self.assertRedirects(response, reverse("post",
                             kwargs={"username": self.user,
                                     "post_id": self.post_two.id}))
        # получаем пост после редактирования
        post_edited = Post.objects.get(id=self.post_two.id)
        self.assertEqual(post_edited.text, form_data["text"])

    def test_not_create_post_unauthorized_client(self):
        '''Проверяем что неавторизованный пользователь не
        не может создать пост'''
        # кол-во постов до добавления
        posts_count = Post.objects.count()
        # подготавливаем данные
        form_data = {
            "text": "This post was created unautorized client",
            "group": self.group_one.id,
        }
        # отправляем пост запрос
        response = self.guest_client.post(reverse("new_post"),
                                          data=form_data)
        # проверяем редирект
        self.assertRedirects(response, reverse("login") + "?next=/new/")
        # проверяем что кол-во постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)

    def test_not_edit_someone_post(self):
        '''Проверяем что авторизованный клиент
        не может отредактировать чужой пост'''
        form_data = {
            "text": "New post edited not author",
            "group": self.group_one.id,
        }
        response = (self.authorized_client_two.
                    post(reverse("post_edit",
                         kwargs={
                                 "username": self.user,
                                 "post_id": self.post_two.id
                                 }),
                         data=form_data,
                         follow=True))
        # проверяем переадресацию
        self.assertRedirects(response, reverse("post",
                             kwargs={
                                 "username": self.user,
                                 "post_id": self.post_two.id
                             }))
        # проверяем что пост не изменился
        self.assertNotEqual(Post.objects.get(id=self.post_two.id).text,
                            form_data["text"])
