from django.test import TestCase
from posts.models import Post, Group, User


class ModelTest(TestCase):
    '''Проверяем модели'''
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # создаем записи в БД
        cls.group = Group.objects.create(
            title="group_one",
            slug="groupone",
            description="This is first group"
        )
        cls.user = User.objects.create_user(username="alex")
        cls.post = Post.objects.create(
            text="a" * 20,
            author=cls.user,
            group=cls.group,
            id=1,
        )

    def test_str_method(self):
        '''Проверяем методы str в моделях'''
        # при отображении модели post выводятся первые
        # 15 символов текста
        post_15 = self.post.text[:15]
        models_data = {
            str(self.group): self.group.title,
            str(self.post): post_15
        }
        for model, expected in models_data.items():
            with self.subTest(model=model):
                self.assertEqual(model, expected)
