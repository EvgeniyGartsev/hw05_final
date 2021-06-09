from django import forms
from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    '''Form for add post'''
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {
            "text": "Текст",
            "group": "Группа",
            "image": "Картинка"
        }
        help_texts = {
            "group": "Группа, в которую необходимо добавить пост"
        }


class CommentForm(ModelForm):
    '''Form for add comments'''
    # меняем способ представления поля текст в шаблоне
    text = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))

    class Meta:
        model = Comment
        fields = ["text"]
        labels = {
            "text": "Комментарий"
        }
