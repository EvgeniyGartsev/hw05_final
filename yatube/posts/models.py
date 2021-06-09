from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE

User = get_user_model()


class Post(models.Model):
    '''Add posts'''
    text = models.TextField()
    pub_date = models.DateTimeField("date_published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey("Group", blank=True, null=True,
                              related_name="group", on_delete=models.SET_NULL)
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        '''Default sort by queries'''
        ordering = ("-pub_date",)
        # название модели в ед.ч
        verbose_name = "запись"
        # название модели во мн.ч
        verbose_name_plural = "записи"

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    '''Groups for posts'''
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=20)
    description = models.TextField()

    class Meta:
        '''Default sort by queries'''
        ordering = ("title",)
        # название модели в ед.ч
        verbose_name = "группа"
        # название модели во мн.ч
        verbose_name_plural = "группы"

    def __str__(self):
        return self.title


class Comment(models.Model):
    '''Comments for posts'''
    post = models.ForeignKey("Post", on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField()
    created = models.DateTimeField("date_created", auto_now_add=True)

    class Meta:
        # сортировка при запросе
        ordering = ("-created",)
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    '''Followers and authors'''
    user = models.ForeignKey(User, on_delete=CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User, on_delete=CASCADE,
                               related_name="following")

    class Meta:
        # сортировка при запросе
        ordering = ("id",)
        verbose_name = "подписчик"
        verbose_name_plural = "подписчики"
        # проверка на уникальность подписки
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name="unique_follow")
        ]
